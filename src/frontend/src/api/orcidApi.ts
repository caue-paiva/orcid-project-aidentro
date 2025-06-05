// ORCID API integration for React frontend

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface OrcidAuthResponse {
  orcid_id: string;
  access_token: string;
  name?: string;
}

export interface OrcidError {
  error: string;
  description?: string;
}

/**
 * Initiates ORCID OAuth flow by redirecting to Django backend
 */
export const initiateOrcidAuth = (scope: string = '/authenticate') => {
  const authUrl = `${BACKEND_URL}/oauth/authorize/?scope=${encodeURIComponent(scope)}`;
  window.location.href = authUrl;
};

/**
 * Check OAuth status from Django backend
 */
export const checkOauthStatus = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/oauth/status/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for session
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to check OAuth status:', error);
    throw error;
  }
};

/**
 * Get current user session from Django backend
 */
export const getCurrentUser = async (): Promise<OrcidAuthResponse | null> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/user/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (response.status === 401) {
      return null; // Not authenticated
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to get current user:', error);
    return null;
  }
};

/**
 * Logout user by clearing Django session
 */
export const logout = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error('Failed to logout:', error);
    return false;
  }
};

/**
 * Utility function to parse URL parameters (for handling auth callbacks)
 */
export const parseUrlParams = (url: string = window.location.href): Record<string, string> => {
  const urlObject = new URL(url);
  const params: Record<string, string> = {};
  
  urlObject.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  
  return params;
}; 