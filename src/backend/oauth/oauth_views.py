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
import concurrent.futures
import threading

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
        # Provide a default email if none is available from ORCID
        email = user_identity.get('email') or f"{orcid_id.replace('-', '')}@orcid.placeholder"
        
        user, created = User.objects.get_or_create(
            orcid_id=orcid_id,
            defaults={
                'username': user_identity.get('name', str(orcid_id)),  # Use ORCID ID as fallback username initially
                'orcid_access_token': access_token,
                'orcid_refresh_token': token_response.get('refresh_token', ''),
                'display_name': user_identity.get('name', ''),
                'email': email,
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
            if not user.email or user.email.endswith('@orcid.placeholder'):
                # Update email if we have a real one, or if current email is placeholder
                if user_identity.get('email'):
                    user.email = user_identity.get('email')
                elif user.email.endswith('@orcid.placeholder'):
                    # Keep the placeholder email if no real email is available
                    pass
            
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

@csrf_exempt
@require_http_methods(["GET"])
def search_researchers(request):
    """
    Search for researchers in the ORCID registry and enrich results with profile data
    
    Query parameters:
    - q: Search query using Solr/Lucene syntax (required)
    - rows: Number of results to return (default: 10, max: 50) - reduced for enrichment
    - start: Starting offset for pagination (default: 0)
    
    Example queries:
    - family-name:Smith
    - given-names:John AND family-name:Doe
    - affiliation-org-name:"University of São Paulo"
    - text:machine learning
    """
    try:
        # Get search query parameter
        query = request.GET.get('q')
        
        if not query:
            return JsonResponse({
                'error': 'Query parameter "q" is required',
                'examples': [
                    'family-name:Smith',
                    'given-names:John AND family-name:Doe',
                    'affiliation-org-name:"University"',
                    'text:"machine learning"'
                ]
            }, status=400)
        
        # Get pagination parameters with adjusted defaults for enrichment
        try:
            rows = int(request.GET.get('rows', 10))
            start = int(request.GET.get('start', 0))
        except ValueError:
            return JsonResponse({
                'error': 'rows and start parameters must be integers'
            }, status=400)
        
        # Validate parameters - reduced max for enrichment
        if rows < 1 or rows > 50:
            return JsonResponse({
                'error': 'rows parameter must be between 1 and 50'
            }, status=400)
        
        if start < 0:
            return JsonResponse({
                'error': 'start parameter must be non-negative'
            }, status=400)
        
      
        # Create ORCID API client for search
        client = ORCIDAPIClient(orcid_id="0000-0000-0000-0000")
        
        # Perform the search
        search_results = client.search_researchers(query=query, rows=rows, start=start)
        
        # Extract relevant information for easier frontend consumption
        formatted_results = {
            'query': query,
            'total_results': search_results.get('num-found', 0),
            'start': start,
            'rows': rows,
            'results': []
        }
        
        # Multi-threaded profile enrichment function
        def fetch_researcher_profile(result):
            """Fetch profile information for a single researcher"""
            orcid_id = result.get('orcid-identifier', {}).get('path')
            
            if not orcid_id:
                return {
                    'orcid_id': None,
                    'orcid_uri': None,
                    'display_name': 'Invalid ORCID ID'
                }
            
            try:
                # Create client for this specific ORCID ID
                profile_client = ORCIDAPIClient(orcid_id=orcid_id)
                
                # Get basic profile information
                person_info = profile_client.get_researcher_person_info()
                
                # Extract name information
                name_info = person_info.get('name', {}) if person_info else {}
                given_names = name_info.get('given-names', {}).get('value') if name_info.get('given-names') else None
                family_name = name_info.get('family-name', {}).get('value') if name_info.get('family-name') else None
                credit_name = name_info.get('credit-name', {}).get('value') if name_info.get('credit-name') else None
                
                # Create display name
                if credit_name:
                    display_name = credit_name
                elif given_names and family_name:
                    display_name = f"{given_names} {family_name}"
                elif family_name:
                    display_name = family_name
                elif given_names:
                    display_name = given_names
                else:
                    display_name = "Name not available"
                
                # Get employment information for current affiliation
                current_affiliation = None
                try:
                    employments = profile_client.get_researcher_employments()
                    if employments and 'affiliation-group' in employments:
                        for group in employments['affiliation-group']:
                            for summary in group.get('summaries', []):
                                employment = summary.get('employment-summary', {})
                                if employment.get('end-date') is None:  # Current employment
                                    org_name = employment.get('organization', {}).get('name')
                                    if org_name:
                                        current_affiliation = org_name
                                        break
                            if current_affiliation:
                                break
                except Exception:
                    pass  # Continue without affiliation info
                
                # Get basic works count
                works_count = 0
                try:
                    works_data = profile_client.get_researcher_works()
                    works_count = len(works_data.get('group', []))
                except Exception:
                    pass
                
                # Build enriched result
                return {
                    'orcid_id': orcid_id,
                    'orcid_uri': f"https://orcid.org/{orcid_id}",
                    'given_names': given_names,
                    'family_name': family_name,
                    'credit_name': credit_name,
                    'display_name': display_name,
                    'current_affiliation': current_affiliation,
                    'works_count': works_count,
                    'profile_url': f"https://orcid.org/{orcid_id}"
                }
                
            except Exception as e:
                # If we can't get profile info, add basic info
                logger.warning(f"Failed to enrich profile for {orcid_id}: {str(e)}")
                return {
                    'orcid_id': orcid_id,
                    'orcid_uri': f"https://orcid.org/{orcid_id}",
                    'given_names': None,
                    'family_name': None,
                    'credit_name': None,
                    'display_name': "Profile not accessible",
                    'current_affiliation': None,
                    'works_count': 0,
                    'profile_url': f"https://orcid.org/{orcid_id}",
                    'error': str(e)
                }

        # Get all search results
        search_result_list = search_results.get('result', [])
        
        # Use ThreadPoolExecutor for concurrent profile fetching
        max_workers = min(len(search_result_list), 8)  # Limit concurrent threads to avoid overwhelming ORCID API
        
        if search_result_list:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all profile fetch tasks
                future_to_result = {
                    executor.submit(fetch_researcher_profile, result): result 
                    for result in search_result_list
                }
                
                # Collect results as they complete, with timeout
                for future in concurrent.futures.as_completed(future_to_result, timeout=30):
                    try:
                        enriched_result = future.result(timeout=10)  # 10 second timeout per individual request
                        formatted_results['results'].append(enriched_result)
                    except concurrent.futures.TimeoutError:
                        logger.warning("Profile fetch timed out for a researcher")
                        # Add basic result for timed out request
                        original_result = future_to_result[future]
                        orcid_id = original_result.get('orcid-identifier', {}).get('path')
                        formatted_results['results'].append({
                            'orcid_id': orcid_id,
                            'orcid_uri': f"https://orcid.org/{orcid_id}" if orcid_id else None,
                            'display_name': "Request timed out",
                            'error': 'timeout'
                        })
                    except Exception as e:
                        logger.error(f"Unexpected error in profile fetch: {str(e)}")
                        # Add basic result for failed request
                        original_result = future_to_result[future]
                        orcid_id = original_result.get('orcid-identifier', {}).get('path')
                        formatted_results['results'].append({
                            'orcid_id': orcid_id,
                            'orcid_uri': f"https://orcid.org/{orcid_id}" if orcid_id else None,
                            'display_name': "Fetch failed",
                            'error': str(e)
                        })
        
        logger.info(f"Successfully searched researchers with query: {query}, found {formatted_results['total_results']} results")
        
        return JsonResponse({
            'success': True,
            'search_results': formatted_results
        })
        
    except Exception as e:
        logger.error(f"Error searching researchers: {str(e)}")
        return JsonResponse({
            'error': 'Failed to search researchers',
            'details': str(e),
            'suggestions': [
                'Check if the search query uses valid Solr/Lucene syntax',
                'Try simplifying the search query',
                'Verify internet connectivity for ORCID API access',
                'Check server logs for detailed error information'
            ]
        }, status=500) 

@csrf_exempt
@require_http_methods(["GET"])
def get_researcher_papers(request):
    """
    Get papers/publications for a given ORCID ID
    
    Query parameters:
    - orcid_id: ORCID identifier (required)
    - format: Response format - 'detailed' or 'summary' (default: 'summary')
    - limit: Maximum number of papers to return (default: 50, max: 200)
    
    Returns:
        JSON response with researcher's papers/publications
    """
    try:
        orcid_id = request.GET.get('orcid_id')
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id parameter is required',
                'example': '/api/researcher-papers/?orcid_id=0000-0000-0000-0000'
            }, status=400)
        
        # Validate ORCID ID format
        if not ORCIDAPIClient.validate_orcid_id_format(orcid_id):
            return JsonResponse({
                'error': 'Invalid ORCID ID format',
                'expected_format': '0000-0000-0000-0000',
                'received': orcid_id
            }, status=400)
        
        # Get format and limit parameters
        response_format = request.GET.get('format', 'summary').lower()
        try:
            limit = int(request.GET.get('limit', 50))
            limit = min(max(1, limit), 200)  # Ensure limit is between 1 and 200
        except ValueError:
            limit = 50
        
        # Create ORCID API client
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        
        # Get researcher's works
        works_data = client.get_researcher_works()
        
        # Format the papers/publications data
        papers = []
        processed_count = 0
        
        for group in works_data.get('group', []):
            if processed_count >= limit:
                break
                
            for work_summary in group.get('work-summary', []):
                if processed_count >= limit:
                    break
                
                # Extract basic information
                title_info = work_summary.get('title', {})
                title = title_info.get('title', {}).get('value', 'Unknown Title') if title_info else 'Unknown Title'
                
                # Extract publication date
                pub_date = work_summary.get('publication-date')
                publication_year = None
                publication_date = None
                
                if pub_date:
                    if pub_date.get('year'):
                        publication_year = int(pub_date['year']['value'])
                    
                    # Build full date if available
                    date_parts = []
                    if pub_date.get('year'):
                        date_parts.append(pub_date['year']['value'])
                    if pub_date.get('month'):
                        date_parts.append(f"{int(pub_date['month']['value']):02d}")
                    if pub_date.get('day'):
                        date_parts.append(f"{int(pub_date['day']['value']):02d}")
                    
                    if len(date_parts) >= 1:
                        publication_date = '-'.join(date_parts)
                
                # Extract journal information
                journal_title = None
                journal_info = work_summary.get('journal-title')
                if journal_info and journal_info.get('value'):
                    journal_title = journal_info['value']
                
                # Extract DOIs and external identifiers
                external_ids = work_summary.get('external-ids', {}).get('external-id', [])
                dois = []
                other_ids = []
                
                for ext_id in external_ids:
                    id_type = ext_id.get('external-id-type', '').lower()
                    id_value = ext_id.get('external-id-value', '')
                    
                    if id_type == 'doi':
                        dois.append(id_value)
                    else:
                        other_ids.append({
                            'type': id_type,
                            'value': id_value
                        })
                
                # Extract URL
                url = None
                url_info = work_summary.get('url')
                if url_info and url_info.get('value'):
                    url = url_info['value']
                
                # Build paper object based on format
                if response_format == 'detailed':
                    paper = {
                        'title': title,
                        'type': work_summary.get('type', 'Unknown'),
                        'publication_year': publication_year,
                        'publication_date': publication_date,
                        'journal': journal_title,
                        'dois': dois,
                        'other_identifiers': other_ids,
                        'url': url,
                        'put_code': work_summary.get('put-code'),
                        'path': work_summary.get('path'),
                        'created_date': work_summary.get('created-date', {}).get('value') if work_summary.get('created-date') else None,
                        'last_modified_date': work_summary.get('last-modified-date', {}).get('value') if work_summary.get('last-modified-date') else None,
                        'source': work_summary.get('source', {}).get('source-name', {}).get('value') if work_summary.get('source') else None,
                        'visibility': work_summary.get('visibility')
                    }
                else:  # summary format
                    paper = {
                        'title': title,
                        'type': work_summary.get('type', 'Unknown'),
                        'publication_year': publication_year,
                        'journal': journal_title,
                        'dois': dois,
                        'url': url
                    }
                
                papers.append(paper)
                processed_count += 1
        
        # Sort papers by publication year (newest first)
        papers.sort(key=lambda x: x.get('publication_year') or 0, reverse=True)
        
        # Build response
        response_data = {
            'success': True,
            'orcid_id': orcid_id,
            'total_works_found': len(works_data.get('group', [])),
            'papers_returned': len(papers),
            'format': response_format,
            'limit_applied': limit,
            'papers': papers
        }
        
        # Add summary statistics
        if papers:
            years = [p.get('publication_year') for p in papers if p.get('publication_year')]
            response_data['statistics'] = {
                'total_papers': len(papers),
                'papers_with_dois': len([p for p in papers if p.get('dois')]),
                'papers_with_journals': len([p for p in papers if p.get('journal')]),
                'publication_years': {
                    'earliest': min(years) if years else None,
                    'latest': max(years) if years else None,
                    'total_years_active': len(set(years)) if years else 0
                },
                'types': {}
            }
            
            # Count paper types
            for paper in papers:
                paper_type = paper.get('type', 'Unknown')
                response_data['statistics']['types'][paper_type] = response_data['statistics']['types'].get(paper_type, 0) + 1
        
        logger.info(f"Successfully retrieved {len(papers)} papers for ORCID ID: {orcid_id}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting researcher papers: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve researcher papers',
            'details': str(e),
            'suggestions': [
                'Verify the ORCID ID format (0000-0000-0000-0000)',
                'Check if the ORCID ID exists and has public data',
                'Try reducing the limit parameter if timeout occurs',
                'Check server logs for detailed error information'
            ]
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_social_media_account(request):
    """
    Add a new social media account to a user with a given ORCID ID
    
    POST body (JSON):
    {
        "orcid_id": "0000-0000-0000-0000",
        "platform": "twitter",  // twitter, instagram, youtube, linkedin, facebook, etc.
        "username": "johndoe",
        "url": "https://twitter.com/johndoe"  // optional, will be generated if not provided
    }
    
    Returns:
        JSON response with success status and updated social media accounts
    """
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body',
                'example': {
                    'orcid_id': '0000-0000-0000-0000',
                    'platform': 'twitter',
                    'username': 'johndoe',
                    'url': 'https://twitter.com/johndoe'
                }
            }, status=400)
        
        # Validate required fields
        orcid_id = data.get('orcid_id')
        platform = data.get('platform')
        username = data.get('username')
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id is required'
            }, status=400)
        
        if not platform:
            return JsonResponse({
                'error': 'platform is required',
                'supported_platforms': ['twitter', 'instagram', 'youtube', 'linkedin', 'facebook', 'github', 'researchgate', 'google_scholar']
            }, status=400)
        
        if not username:
            return JsonResponse({
                'error': 'username is required'
            }, status=400)
        
        # Validate ORCID ID format
        if not ORCIDAPIClient.validate_orcid_id_format(orcid_id):
            return JsonResponse({
                'error': 'Invalid ORCID ID format',
                'expected_format': '0000-0000-0000-0000',
                'received': orcid_id
            }, status=400)
        
        # Find user by ORCID ID, create if not found
        try:
            user = User.objects.get(orcid_id=orcid_id)
            user_created = False
        except User.DoesNotExist:
            # Create new user with template data
            clean_orcid = orcid_id.replace('-', '')
            template_username = f"user_{clean_orcid[-8:]}"  # Use last 8 digits of ORCID
            template_email = f"{clean_orcid}@orcid.placeholder"
            
            user = User.objects.create_user(
                username=template_username,
                email=template_email,
                orcid_id=orcid_id,
                display_name=f"ORCID User {orcid_id}",
                social_media_accounts=[]
            )
            user_created = True
            logger.info(f"Created new user with ORCID ID: {orcid_id}, username: {template_username}")
        
        # Generate URL if not provided
        url = data.get('url')
        if not url:
            url = _generate_social_media_url(platform, username)
        
        # Validate platform
        supported_platforms = [
            'twitter', 'x', 'instagram', 'youtube', 'linkedin', 
            'facebook', 'github', 'researchgate', 'google_scholar', 
            'orcid', 'mastodon', 'tiktok', 'snapchat'
        ]
        
        if platform.lower() not in supported_platforms:
            return JsonResponse({
                'error': f'Unsupported platform: {platform}',
                'supported_platforms': supported_platforms
            }, status=400)
        
        # Create new social media account entry
        new_account = {
            'platform': platform.lower(),
            'username': username,
            'url': url,
            'added_at': timezone.now().isoformat()
        }
        
        # Get current social media accounts
        current_accounts = user.social_media_accounts or []
        
        # Check if account already exists for this platform
        existing_account_index = None
        for i, account in enumerate(current_accounts):
            if account.get('platform') == platform.lower():
                existing_account_index = i
                break
        
        if existing_account_index is not None:
            # Update existing account
            current_accounts[existing_account_index] = new_account
            action = 'updated'
        else:
            # Add new account
            current_accounts.append(new_account)
            action = 'added'
        
        # Update user's social media accounts
        user.social_media_accounts = current_accounts
        user.save()
        
        logger.info(f"Successfully {action} {platform} account for user {user.username} (ORCID: {orcid_id})")
        
        return JsonResponse({
            'success': True,
            'action': action,
            'user_created': user_created,
            'orcid_id': orcid_id,
            'platform': platform.lower(),
            'username': username,
            'url': url,
            'total_accounts': len(current_accounts),
            'all_accounts': current_accounts,
            'user_info': {
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email
            }
        })
        
    except Exception as e:
        logger.error(f"Error adding social media account: {str(e)}")
        return JsonResponse({
            'error': 'Failed to add social media account',
            'details': str(e)
        }, status=500)


def _generate_social_media_url(platform: str, username: str) -> str:
    """
    Generate social media URL based on platform and username
    
    Args:
        platform: Social media platform name
        username: Username on the platform
        
    Returns:
        Generated URL for the social media account
    """
    platform = platform.lower()
    
    url_patterns = {
        'twitter': f'https://twitter.com/{username}',
        'x': f'https://x.com/{username}',
        'instagram': f'https://instagram.com/{username}',
        'youtube': f'https://youtube.com/@{username}',
        'linkedin': f'https://linkedin.com/in/{username}',
        'facebook': f'https://facebook.com/{username}',
        'github': f'https://github.com/{username}',
        'researchgate': f'https://researchgate.net/profile/{username}',
        'google_scholar': f'https://scholar.google.com/citations?user={username}',
        'orcid': f'https://orcid.org/{username}',
        'mastodon': f'https://mastodon.social/@{username}',  # Default instance
        'tiktok': f'https://tiktok.com/@{username}',
        'snapchat': f'https://snapchat.com/add/{username}'
    }
    
    return url_patterns.get(platform, f'https://{platform}.com/{username}')


@csrf_exempt
@require_http_methods(["GET"])
def get_social_media_accounts(request):
    """
    Get social media accounts for a user with a given ORCID ID
    
    Query parameters:
    - orcid_id: ORCID identifier (required)
    
    Returns:
        JSON response with user's social media accounts
    """
    try:
        orcid_id = request.GET.get('orcid_id')
        
        if not orcid_id:
            return JsonResponse({
                'error': 'orcid_id parameter is required',
                'example': '/api/get-social-media/?orcid_id=0000-0000-0000-0000'
            }, status=400)
        
        # Validate ORCID ID format
        if not ORCIDAPIClient.validate_orcid_id_format(orcid_id):
            return JsonResponse({
                'error': 'Invalid ORCID ID format',
                'expected_format': '0000-0000-0000-0000',
                'received': orcid_id
            }, status=400)
        
        # Find user by ORCID ID
        try:
            user = User.objects.get(orcid_id=orcid_id)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found with the provided ORCID ID',
                'orcid_id': orcid_id,
                'suggestion': 'User may not have been created yet. Try adding a social media account first.'
            }, status=404)
        
        # Get social media accounts
        social_media_accounts = user.social_media_accounts or []
        
        # Sort accounts by platform name for consistent ordering
        social_media_accounts.sort(key=lambda x: x.get('platform', ''))
        
        # Build response with user info and social media accounts
        response_data = {
            'success': True,
            'orcid_id': orcid_id,
            'user_info': {
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'profile_public': user.profile_public,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_orcid_sync': user.last_orcid_sync.isoformat() if user.last_orcid_sync else None
            },
            'social_media_accounts': social_media_accounts,
            'total_accounts': len(social_media_accounts),
            'platforms': [account.get('platform') for account in social_media_accounts]
        }
        
        # Add statistics about social media presence
        if social_media_accounts:
            platform_counts = {}
            for account in social_media_accounts:
                platform = account.get('platform', 'unknown')
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            response_data['statistics'] = {
                'most_recent_addition': max(
                    social_media_accounts, 
                    key=lambda x: x.get('added_at', '1970-01-01')
                ).get('added_at') if social_media_accounts else None,
                'platform_distribution': platform_counts,
                'has_professional_accounts': any(
                    account.get('platform') in ['linkedin', 'researchgate', 'google_scholar', 'github']
                    for account in social_media_accounts
                ),
                'has_social_accounts': any(
                    account.get('platform') in ['twitter', 'x', 'instagram', 'facebook', 'youtube']
                    for account in social_media_accounts
                )
            }
        else:
            response_data['statistics'] = {
                'most_recent_addition': None,
                'platform_distribution': {},
                'has_professional_accounts': False,
                'has_social_accounts': False
            }
        
        logger.info(f"Successfully retrieved {len(social_media_accounts)} social media accounts for ORCID ID: {orcid_id}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting social media accounts: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve social media accounts',
            'details': str(e)
        }, status=500) 