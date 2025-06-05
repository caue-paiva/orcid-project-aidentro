import secrets
import urllib.parse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.shortcuts import redirect
from decouple import config
from .oauth_services import exchange_authorization_code
import logging

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
    This automatically exchanges the authorization code for tokens
    and creates/logs in the user.
    
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
        logger.info(f"Access Token: {access_token}")
        logger.info(f"ORCID ID: {orcid_id}")
        
        # Here you would typically:
        # 1. Create or get user from database
        # 2. Store the access token (encrypted)
        # 3. Log the user in
        # 4. Redirect to frontend with success
        
        # For now, we'll store in session and redirect
        request.session['orcid_id'] = orcid_id
        request.session['orcid_access_token'] = access_token
        request.session['orcid_name'] = token_response.get('name', '')
        
        # Redirect to frontend with success
        frontend_url = config('FRONTEND_URL', default='http://localhost:8080')
        return redirect(f"{frontend_url}/auth/success?orcid_id={orcid_id}")
        
    except Exception as e:
        logger.error(f"Failed to exchange authorization code: {str(e)}")
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