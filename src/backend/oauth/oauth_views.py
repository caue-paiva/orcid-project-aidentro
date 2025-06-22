import secrets
import urllib.parse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.shortcuts import redirect
from decouple import config
from .oauth_services import exchange_authorization_code
import logging
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from config.models import User, CitationTimeSeries, Work
from django.utils import timezone
from datetime import datetime

# Add import for our ORCID API client
from integrations.orcid_api import ORCIDAPIClient

logger = logging.getLogger(__name__)

# ORCID OAuth Configuration
ORCID_BASE_URL = config('ORCID_BASE_URL', default='https://orcid.org')
ORCID_CLIENT_ID = config('ORCID_CLIENT_ID')
ORCID_CLIENT_SECRET = config('ORCID_CLIENT_SECRET')
ORCID_REDIRECT_URI = config('ORCID_REDIRECT_URI')
"""
Views for implementing the OAuth flow with the orcid API

1) oauth_authorize: handles the user authorization of our application getting their Orcid ID. Redirects user to the orcid authorize page 

2) oauth_callback: serves the redirect URI, after the user accepts or denies access, he/she will be sent back that URI and this view will be called, which takes
the returned access code and automatically exchanges for an access token and creates the user Session

3) oauth_status

"""

@require_http_methods(["GET"])
def oauth_authorize(request):
    """
    GET /oauth/authorize
    
    Redirects user to ORCID authorization page where they can grant permission
    to access their ORCID iD and public data.
    
    Query parameters:
    - scope: OAuth scope (default: /authenticate)
    - state: Optional state parameter for CSRF protection
    """
    
    # Get scope from query params, default to /authenticate
    scope = request.GET.get('scope', '/authenticate')
    
    # Generate state parameter for CSRF protection if not provided
    state = request.GET.get('state', secrets.token_urlsafe(32))
    
    # Build ORCID authorization URL
    auth_params = {
        'client_id': ORCID_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': ORCID_REDIRECT_URI,
        'state': state
    }
    
    # Add optional parameters if provided
    if request.GET.get('given_names'):
        auth_params['given_names'] = request.GET.get('given_names')
    if request.GET.get('family_names'):
        auth_params['family_names'] = request.GET.get('family_names')
    if request.GET.get('email'):
        auth_params['email'] = request.GET.get('email')
    if request.GET.get('orcid'):
        auth_params['orcid'] = request.GET.get('orcid')
    
    # Construct the authorization URL
    auth_url = f"{ORCID_BASE_URL}/oauth/authorize?" + urllib.parse.urlencode(auth_params)
    
    return HttpResponseRedirect(auth_url)

@require_http_methods(["GET"])
def oauth_callback(request):
    """
    This view MUST be associated with the redirect URI
    
    Handles the redirect from ORCID after user authorization.
    This automatically exchanges the authorization code for tokens,
    creates/updates the user in database, and logs them in.
    
    Query parameters:
    - code: Authorization code from ORCID
    - state: State parameter for CSRF protection
    - error: Error code if authorization failed
    - error_description: Human-readable error description
    """
    
    # Check for errors
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description', 'Authorization failed')
        logger.error(f"ORCID authorization error: {error} - {error_description}")
        
        # Redirect to frontend with error
        frontend_url = config('FRONTEND_URL', default='http://localhost:8080')
        return redirect(f"{frontend_url}/auth/error?error={error}&description={error_description}")
    
    # Get authorization code
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        logger.error("No authorization code received from ORCID")
        frontend_url = config('FRONTEND_URL', default='http://localhost:8080')
        return redirect(f"{frontend_url}/auth/error?error=no_code")
    
    try:
        # Exchange authorization code for access token and ORCID iD
        access_token, orcid_id, token_response = exchange_authorization_code(
            code, 
            ORCID_REDIRECT_URI
        )
        
        logger.info(f"Successfully authenticated user with ORCID iD: {orcid_id}")
        
        # Get user identity information from ORCID API
        orcid_client = ORCIDAPIClient(access_token=access_token, orcid_id=orcid_id)
        user_identity = orcid_client.get_user_identity_info()
        
        # Create or update user in database
        user, created = User.objects.get_or_create(
            orcid_id=orcid_id,
            defaults={
                'username': user_identity.get('name', str(orcid_id)),  # Use ORCID ID as fallback username initially
                'orcid_access_token': access_token,
                'orcid_refresh_token': token_response.get('refresh_token', ''),
                'display_name': user_identity.get('name', ''),
                'email': user_identity.get('email', ''),
                'last_orcid_sync': timezone.now()
            }
        )
        
        if not created:
            # Update existing user with new token and info
            user.orcid_access_token = access_token
            user.orcid_refresh_token = token_response.get('refresh_token', '')
            user.last_orcid_sync = timezone.now()
            
            # Update display name and email if they're empty or different
            if not user.display_name and user_identity.get('name'):
                user.display_name = user_identity.get('name')
            if not user.email and user_identity.get('email'):
                user.email = user_identity.get('email')
            
            user.save()
            logger.info(f"Updated existing user: {user.username} ({orcid_id})")
        else:
            logger.info(f"Created new user: {user.username} ({orcid_id})")
        
        # Log the user in
        login(request, user)
        
        # Store additional session data for compatibility
        request.session['orcid_id'] = orcid_id
        request.session['orcid_access_token'] = access_token
        request.session['orcid_name'] = user_identity.get('name', '')
        
        # Force session save and log session details
        request.session.save()
        logger.info(f"Session saved with key: {request.session.session_key}")
        logger.info(f"User logged in: {user.username}")
        
        # Populate database with user's publication data (asynchronously)
        if created or not user.last_orcid_sync:
            logger.info(f"🔄 Starting background population of publication data for {user.username}")
            try:
                # Import here to avoid circular imports
                from django.core.management import call_command
                import threading
                
                def populate_user_data():
                    """Background task to populate user data"""
                    try:
                        logger.info(f"📚 Populating publications for ORCID ID: {orcid_id}")
                        call_command('populate_user_with_citations', 
                                   orcid_id=orcid_id, 
                                   max_publications=15,
                                   skip_citations=False,
                                   force=True,  # Update existing user data
                                   verbosity=0)  # Reduce verbosity for background task
                        logger.info(f"✅ Successfully populated data for {user.username}")
                    except Exception as e:
                        logger.error(f"❌ Failed to populate data for {user.username}: {str(e)}")
                
                # Start background thread to populate data
                thread = threading.Thread(target=populate_user_data)
                thread.daemon = True  # Thread will die when main program exits
                thread.start()
                
            except Exception as e:
                logger.error(f"Failed to start background population: {str(e)}")
        
        # Redirect to frontend with success
        frontend_url = config('FRONTEND_URL', default='http://localhost:8080')
        return redirect(f"{frontend_url}/auth/success?orcid_id={orcid_id}")
        
    except Exception as e:
        logger.error(f"Failed to exchange authorization code or create user: {str(e)}")
        frontend_url = config('FRONTEND_URL', default='http://localhost:8080')
        return redirect(f"{frontend_url}/auth/error?error=token_exchange_failed")

@require_http_methods(["GET"])
def oauth_status(request):
    """
    GET /oauth/status
    
    Returns the current OAuth configuration status (for debugging/health checks)
    """
    
    config_status = {
        'orcid_base_url': ORCID_BASE_URL,
        'client_id_configured': bool(ORCID_CLIENT_ID),
        'client_secret_configured': bool(ORCID_CLIENT_SECRET),
        'redirect_uri_configured': bool(ORCID_REDIRECT_URI),
        'endpoints': {
            'authorize': '/oauth/authorize',
            'token': '/oauth/token',
            'callback': '/oauth/callback'
        }
    }
    
    return JsonResponse(config_status)

@csrf_exempt
@require_http_methods(["GET"])
def get_user_identity(request):
    """
    Get user identity information from ORCID API
    Expects orcid_id as a query parameter
    """
    try:
        orcid_id = request.GET.get('orcid_id')
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id parameter is required'
            }, status=400)
        
        # Create ORCID API client (no access token needed for public API)
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        
        # Get user identity information
        user_identity = client.get_user_identity_info()
        
        logger.info(f"Successfully retrieved user identity for ORCID ID: {orcid_id}")
        
        return JsonResponse({
            'success': True,
            'user_identity': user_identity
        })
        
    except Exception as e:
        logger.error(f"Error getting user identity: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve user identity',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_citation_metrics(request):
    """
    Get citation metrics for dashboard display
    Expects orcid_id as a query parameter
    """
    try:
        orcid_id = request.GET.get('orcid_id')
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id parameter is required'
            }, status=400)
        
        # Create ORCID API client
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        
        # Get citation metrics for dashboard
        citation_metrics = client.get_citation_metrics_for_dashboard()

        user = User.objects.filter(orcid_id=orcid_id).first()

        if user:
            ts_qs = (
                CitationTimeSeries.objects
                    .filter(user=user)
                    .order_by("year")
            )

            if ts_qs.exists():
                yearly_data = [
                    {"year": ts.year, "citations": ts.citations_count}
                    for ts in ts_qs
                ]

                total_citations = ts_qs.aggregate(
                    total=Sum("citations_count")
                )["total"] or 0

                current_year = datetime.now().year
                cur_year_cit = next(
                    (d["citations"] for d in yearly_data
                    if d["year"] == current_year), 0)
                prev_year_cit = next(
                    (d["citations"] for d in yearly_data
                    if d["year"] == current_year - 1), 0)

                citation_trend = None
                if prev_year_cit > 0:
                    pct = round(
                        ((cur_year_cit - prev_year_cit) / prev_year_cit) * 100,
                        1,
                    )
                    citation_trend = {"value": abs(pct), "isPositive": pct >= 0}

                years_with_cit = [d for d in yearly_data if d["citations"] > 0]
                avg_cit_per_year = (
                    round(total_citations / len(years_with_cit))
                    if years_with_cit else 0
                )

                total_pubs = Work.objects.filter(authors__user=user).count()
                pubs_with_cit = Work.objects.filter(
                    authors__user=user, citation_count__gt=0
                ).count()

                h_idx_approx = min(
                    pubs_with_cit,
                    int(total_citations / max(pubs_with_cit, 1)),
                )

                citation_metrics = {
                    "total_citations": total_citations,
                    "citation_trend": citation_trend,
                    "avg_citations_per_year": avg_cit_per_year,
                    "h_index_approximation": h_idx_approx,
                    "publications_count": total_pubs,
                    "cited_publications_count": pubs_with_cit,
                    "citation_chart_data": yearly_data,
                    "analysis_success": True,
                }

                logger.info(
                    "Citation metrics served from DB for ORCID %s", orcid_id
                )
                return JsonResponse(
                    {"success": True, "citation_metrics": citation_metrics}
                )

        logger.info("User not found in database, fetching from ORCID API")
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        citation_metrics = client.get_citation_metrics_for_dashboard()

        logger.info(f"Successfully retrieved citation metrics for ORCID ID: {orcid_id}")
        
        return JsonResponse({
            'success': True,
            'citation_metrics': citation_metrics
        })
        
    except Exception as e:
        logger.error(f"Error getting citation metrics: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve citation metrics',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_citation_analysis(request):
    """
    Get detailed citation analysis data
    Expects orcid_id as a query parameter
    Optional: years_back parameter (default: 5)
    """
    try:
        orcid_id = request.GET.get('orcid_id')
        years_back = int(request.GET.get('years_back', 5))
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id parameter is required'
            }, status=400)
        
        # Create ORCID API client
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        
        # Get detailed citation analysis
        citation_analysis = client.get_citation_analysis(years_back=years_back)
        
        logger.info(f"Successfully retrieved citation analysis for ORCID ID: {orcid_id}")
        
        return JsonResponse({
            'success': True,
            'citation_analysis': citation_analysis
        })
        
    except Exception as e:
        logger.error(f"Error getting citation analysis: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve citation analysis',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def test_citation_analysis(request):
    """
    Test endpoint with hardcoded ORCID ID for quick testing
    """
    try:
        # Hardcoded test ORCID ID
        test_orcid_id = "0000-0003-1574-0784"
        years_back = int(request.GET.get('years_back', 5))
        max_publications = int(request.GET.get('max_publications', 10))  # Reduced default for faster testing
        
        # Create ORCID API client
        client = ORCIDAPIClient(access_token="", orcid_id=test_orcid_id)
        
        # Get user identity first (quick operation)
        user_identity = client.get_user_identity_info()
        
        # Get citation analysis with limits to prevent timeout
        citation_analysis = client.get_citation_analysis(
            years_back=years_back, 
            max_publications=max_publications,
            timeout_per_request=8  # 8 second timeout per CrossRef request
        )
        
        # Get citation metrics for dashboard
        citation_metrics = client.get_citation_metrics_for_dashboard()
        
        return JsonResponse({
            'success': True,
            'test_orcid_id': test_orcid_id,
            'user_identity': user_identity,
            'citation_metrics': citation_metrics,
            'citation_analysis': citation_analysis,
            'performance': {
                'analysis_time_seconds': citation_analysis.get('analysis_time_seconds', 0),
                'publications_analyzed': citation_analysis['successful_lookups'],
                'publications_found': citation_analysis['total_publications'],
                'limited_analysis': citation_analysis.get('limited_analysis', False)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in test citation analysis: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve test citation data',
            'details': str(e),
            'suggestions': [
                'Check if backend server is running',
                'Verify internet connectivity for ORCID/CrossRef APIs',
                'Try reducing max_publications parameter',
                'Check server logs for detailed error information'
            ]
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def quick_citation_test(request):
    """
    Very quick citation test with minimal data for fast response
    """
    try:
        test_orcid_id = "0000-0003-1574-0784"
        
        # Create ORCID API client
        client = ORCIDAPIClient(access_token="", orcid_id=test_orcid_id)
        
        # Get user identity only (no citation analysis)
        user_identity = client.get_user_identity_info()
        
        # Get basic works info without citation counts
        works_data = client.get_researcher_works()
        total_works = len(works_data.get('group', []))
        
        return JsonResponse({
            'success': True,
            'test_orcid_id': test_orcid_id,
            'user_identity': user_identity,
            'basic_stats': {
                'total_works': total_works,
                'test_type': 'quick_test_no_citations'
            },
            'message': 'Quick test successful - user data retrieved without citation analysis'
        })
        
    except Exception as e:
        logger.error(f"Error in quick citation test: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve quick test data',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_current_user_identity(request):
    """
    Get current authenticated user's identity information
    Uses Django authenticated user or falls back to session data
    """
    try:
        # Debug: Log request details
        logger.info(f"Request from: {request.META.get('HTTP_ORIGIN', 'Unknown origin')}")
        logger.info(f"Django user authenticated: {request.user.is_authenticated}")
        logger.info(f"Session key: {request.session.session_key}")
        
        # Try to get user from Django authentication first
        if request.user.is_authenticated and hasattr(request.user, 'orcid_id') and request.user.orcid_id:
            user = request.user
            orcid_id = user.orcid_id
            access_token = user.orcid_access_token or ''
            
            logger.info(f"Using Django authenticated user: {user.username} ({orcid_id})")
            
            # Create ORCID API client
            client = ORCIDAPIClient(access_token=access_token, orcid_id=orcid_id)
            
            # Get user identity information
            user_identity = client.get_user_identity_info()
            
            # Add Django user info
            user_identity['authenticated'] = True
            user_identity['user_id'] = str(user.id)
            user_identity['username'] = user.username
            user_identity['display_name'] = user.display_name
            user_identity['last_orcid_sync'] = user.last_orcid_sync.isoformat() if user.last_orcid_sync else None
            
            logger.info(f"Successfully retrieved current user identity for Django user: {user.username}")
            
            return JsonResponse({
                'success': True,
                'user_identity': user_identity
            })
        
        # Fallback to session-based authentication
        orcid_id = request.session.get('orcid_id')
        
        if not orcid_id:
            logger.info(f"No authenticated user found. Session keys: {list(request.session.keys())}")
            return JsonResponse({
                'error': 'No authenticated ORCID user found',
                'authenticated': False,
                'debug_info': {
                    'session_key': request.session.session_key,
                    'session_keys': list(request.session.keys()),
                    'django_user_authenticated': request.user.is_authenticated,
                    'origin': request.META.get('HTTP_ORIGIN', 'Unknown')
                }
            }, status=401)
        
        # Create ORCID API client with session data
        access_token = request.session.get('orcid_access_token', '')
        client = ORCIDAPIClient(access_token=access_token, orcid_id=orcid_id)
        
        # Get user identity information
        user_identity = client.get_user_identity_info()
        
        # Add session info
        user_identity['authenticated'] = True
        user_identity['session_data'] = {
            'access_token_available': bool(access_token),
            'session_orcid_id': orcid_id
        }
        
        logger.info(f"Successfully retrieved current user identity from session for ORCID ID: {orcid_id}")
        
        return JsonResponse({
            'success': True,
            'user_identity': user_identity
        })
        
    except Exception as e:
        logger.error(f"Error getting current user identity: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve current user identity',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def debug_session(request):
    """
    Debug endpoint to check session data
    """
    return JsonResponse({
        'session_data': dict(request.session),
        'session_keys': list(request.session.keys()),
        'has_orcid_id': 'orcid_id' in request.session,
        'has_access_token': 'orcid_access_token' in request.session,
        'session_key': request.session.session_key,
        'cookies': dict(request.COOKIES),
        'origin': request.META.get('HTTP_ORIGIN', 'Unknown'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
    })

@csrf_exempt  
@require_http_methods(["GET", "OPTIONS"])
def health_check(request):
    """
    Simple health check endpoint
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'preflight_ok'})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    from django.conf import settings
    return JsonResponse({
        'status': 'ok',
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'cors_allow_all_origins': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
        'cors_allowed_origins': getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
        'session_key_exists': bool(request.session.session_key),
        'request_origin': request.META.get('HTTP_ORIGIN', 'Unknown'),
        'has_any_session_data': bool(dict(request.session)),
        'oauth_config': {
            'orcid_base_url': ORCID_BASE_URL,
            'client_id_configured': bool(ORCID_CLIENT_ID),
            'redirect_uri': ORCID_REDIRECT_URI,
            'frontend_url': config('FRONTEND_URL', default='http://localhost:8080'),
        }
    })

@csrf_exempt  
def simple_test(request):
    """
    Super simple test endpoint to debug CORS
    """
    response = JsonResponse({
        'message': 'Simple test endpoint working',
        'method': request.method,
        'origin': request.META.get('HTTP_ORIGIN', 'Unknown'),
    })
    
    # Manually add CORS headers
    origin = request.META.get('HTTP_ORIGIN')
    if origin:
        response['Access-Control-Allow-Origin'] = origin
    else:
        response['Access-Control-Allow-Origin'] = '*'
        
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response['Access-Control-Allow-Credentials'] = 'true'
    
    return response 