"""
OAuth service functions for ORCID integration.

These functions handle the backend OAuth operations like token exchange,
token validation, and user authentication flow.
"""

import json
import requests
from typing import Dict, Optional, Tuple
from decouple import config
import logging

logger = logging.getLogger(__name__)

# ORCID OAuth Configuration
ORCID_BASE_URL = config('ORCID_BASE_URL', default='https://orcid.org')
ORCID_CLIENT_ID = config('ORCID_CLIENT_ID')
ORCID_CLIENT_SECRET = config('ORCID_CLIENT_SECRET')
ORCID_REDIRECT_URI = config('ORCID_REDIRECT_URI')


def exchange_authorization_code(authorization_code: str, redirect_uri: str) -> Tuple[str, str, Dict]:
    """
    Exchange authorization code for access token and ORCID iD.
    
    Args:
        authorization_code: The authorization code from ORCID callback
        redirect_uri: The redirect URI used in the authorization request
        
    Returns:
        Tuple of (access_token, orcid_id, full_response)
        
    Raises:
        Exception: If token exchange fails
    """
    token_data = {
        'client_id': ORCID_CLIENT_ID,
        'client_secret': ORCID_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }
    
    token_url = f"{ORCID_BASE_URL}/oauth/token"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(
            token_url,
            data=token_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            token_response = response.json()
            
            # Validate ORCID iD
            orcid_id = token_response.get('orcid')
            if not orcid_id or not _validate_orcid_id(orcid_id):
                raise Exception("Invalid or missing ORCID iD in token response")
            
            logger.info(f"Successfully exchanged code for token. ORCID iD: {orcid_id}")
            
            # Return parsed values
            return (
                token_response['access_token'],
                token_response['orcid'],
                token_response
            )
        else:
            error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.RequestException as e:
        error_msg = f"Failed to communicate with ORCID: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def get_client_credentials_token(scope: str = '/read-public') -> Dict:
    """
    Get client credentials token for backend operations.
    
    Args:
        scope: OAuth scope (default: /read-public)
        
    Returns:
        Dictionary containing access_token, token_type, etc.
        
    Raises:
        Exception: If token request fails
    """
    token_data = {
        'client_id': ORCID_CLIENT_ID,
        'client_secret': ORCID_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': scope
    }
    
    token_url = f"{ORCID_BASE_URL}/oauth/token"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(
            token_url,
            data=token_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            token_response = response.json()
            logger.info("Successfully obtained client credentials token")
            return token_response
        else:
            error_msg = f"Client credentials request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.RequestException as e:
        error_msg = f"Failed to communicate with ORCID: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def validate_access_token(access_token: str) -> bool:
    """
    Validate an access token by making a test request to ORCID API.
    
    Args:
        access_token: The access token to validate
        
    Returns:
        True if token is valid, False otherwise
    """
    try:
        # Convert base URL to API URL
        if 'sandbox.orcid.org' in ORCID_BASE_URL:
            api_base_url = 'https://pub.sandbox.orcid.org/v3.0'
        else:
            api_base_url = 'https://pub.orcid.org/v3.0'
        
        # Make a simple search request
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{api_base_url}/search/",
            headers=headers,
            params={'q': 'family-name:test', 'rows': 1},
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        return False

def _validate_orcid_id(orcid_id: str) -> bool:
    """
    Validate ORCID iD format.
    
    Args:
        orcid_id: ORCID identifier to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    import re
    
    if not orcid_id:
        return False
    
    # Remove any URI prefix if present
    if orcid_id.startswith('https://orcid.org/'):
        orcid_id = orcid_id.replace('https://orcid.org/', '')
    elif orcid_id.startswith('http://orcid.org/'):
        orcid_id = orcid_id.replace('http://orcid.org/', '')
    
    # Check format: 0000-0000-0000-000X
    pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
    return bool(re.match(pattern, orcid_id))