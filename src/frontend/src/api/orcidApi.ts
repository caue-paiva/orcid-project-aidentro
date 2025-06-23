// ORCID API integration for React frontend

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

console.log('🔧 ORCID API: Using backend URL:', BACKEND_URL);

export interface OrcidAuthResponse {
  orcid_id: string;
  access_token: string;
  name?: string;
}

export interface OrcidError {
  error: string;
  description?: string;
}

export interface UserIdentity {
  orcid_id: string;
  name: string;
  email?: string;
  current_affiliation?: string;
  current_location?: string;
  profile_url: string;
  authenticated?: boolean;
  session_data?: {
    access_token_available: boolean;
    session_orcid_id: string;
  };
}

export interface UserIdentityResponse {
  success: boolean;
  user_identity: UserIdentity;
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
 * Get user identity information from ORCID API by ORCID ID
 */
export const getUserIdentity = async (orcidId: string): Promise<UserIdentity> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/user-identity/?orcid_id=${encodeURIComponent(orcidId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: UserIdentityResponse = await response.json();
    
    if (!data.success) {
      throw new Error('Failed to retrieve user identity');
    }

    return data.user_identity;
  } catch (error) {
    console.error('Failed to get user identity:', error);
    throw error;
  }
};

/**
 * Get current authenticated user's identity information
 */
export const getCurrentUserIdentity = async (): Promise<UserIdentity | null> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/current-user-identity/`, {
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

    const data: UserIdentityResponse = await response.json();
    
    if (!data.success) {
      throw new Error('Failed to retrieve current user identity');
    }

    return data.user_identity;
  } catch (error) {
    console.error('Failed to get current user identity:', error);
    return null;
  }
};

/**
 * Health check function to test basic connectivity
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to check health:', error);
    throw error;
  }
};

/**
 * Debug function to check session data
 */
export const debugSession = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/debug-session/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to debug session:', error);
    throw error;
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

/**
 * Get citation metrics for dashboard display
 */
export const getCitationMetrics = async (orcidId: string) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/citation-metrics/?orcid_id=${encodeURIComponent(orcidId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to retrieve citation metrics');
    }

    return data.citation_metrics;
  } catch (error) {
    console.error('Failed to get citation metrics:', error);
    throw error;
  }
};

/**
 * Get detailed citation analysis data
 */
export const getCitationAnalysis = async (orcidId: string, yearsBack: number = 5) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/citation-analysis/?orcid_id=${encodeURIComponent(orcidId)}&years_back=${yearsBack}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to retrieve citation analysis');
    }

    return data.citation_analysis;
  } catch (error) {
    console.error('Failed to get citation analysis:', error);
    throw error;
  }
};

/**
 * Test citation analysis with hardcoded ORCID ID
 */
export const testCitationAnalysis = async (yearsBack: number = 5) => {
  const url = `${BACKEND_URL}/api/test-citation-analysis/?years_back=${yearsBack}`;
  console.log('🚀 Making API call to:', url);
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    console.log('📡 Response status:', response.status);
    console.log('📡 Response ok:', response.ok);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Response error:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const data = await response.json();
    console.log('📦 Received data:', data);
    
    if (!data.success) {
      console.error('❌ API returned success=false:', data);
      throw new Error(data.error || 'Failed to retrieve test citation data');
    }

    const result = {
      testOrcidId: data.test_orcid_id,
      userIdentity: data.user_identity,
      citationMetrics: data.citation_metrics,
      citationAnalysis: data.citation_analysis
    };

    console.log('✅ Returning formatted result:', result);
    return result;
  } catch (error) {
    console.error('💥 Failed to test citation analysis:', error);
    throw error;
  }
};

// New search researchers function
export interface SearchResearchersParams {
  q: string;
  rows?: number;
  start?: number;
}

export interface SearchResearchersResponse {
  success: boolean;
  search_results: {
    query: string;
    total_results: number;
    start: number;
    rows: number;
    results: Array<{
      orcid_id: string;
      orcid_uri: string;
      given_names?: string;
      family_name?: string;
      credit_name?: string;
      display_name: string;
      current_affiliation?: string;
      works_count?: number;
      profile_url: string;
      error?: string;
    }>;
  };
  error?: string;
}

export const searchResearchers = async (params: SearchResearchersParams): Promise<SearchResearchersResponse> => {
  try {
    const queryParams = new URLSearchParams();
    queryParams.append('q', params.q);
    
    if (params.rows) {
      queryParams.append('rows', params.rows.toString());
    }
    
    if (params.start) {
      queryParams.append('start', params.start.toString());
    }

    const response = await fetch(`${BACKEND_URL}/api/search-researchers/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching researchers:', error);
    throw error;
  }
};

// Researcher papers API
export interface ResearcherPaper {
  title: string;
  type: string;
  publication_year: number;
  journal: string;
  dois: string[];
  url?: string;
}

export interface ResearcherPapersResponse {
  success: boolean;
  orcid_id: string;
  total_works_found: number;
  papers_returned: number;
  format: string;
  limit_applied: number;
  papers: ResearcherPaper[];
  statistics: {
    total_papers: number;
    papers_with_dois: number;
    papers_with_journals: number;
    publication_years: {
      earliest: number;
      latest: number;
      total_years_active: number;
    };
    types: Record<string, number>;
  };
}

export const getResearcherPapers = async (orcidId: string, limit: number = 50): Promise<ResearcherPapersResponse> => {
  try {
    const queryParams = new URLSearchParams({
      orcid_id: orcidId,
      limit: limit.toString(),
    });

    console.log('📄 Fetching researcher papers for ORCID ID:', orcidId);
    
    const response = await fetch(`${BACKEND_URL}/api/researcher-papers/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Researcher papers received:', data);
    
    return data;
  } catch (error) {
    console.error('❌ Error fetching researcher papers:', error);
    throw error;
  }
}; 