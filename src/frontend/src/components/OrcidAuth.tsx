import React, { useEffect, useState } from 'react';
import { initiateOrcidAuth, getCurrentUser, logout, parseUrlParams } from '../api/orcidApi';

interface User {
  orcid_id: string;
  name?: string;
}

const OrcidAuth: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Check if we're returning from OAuth callback
        const urlParams = parseUrlParams();
        
        if (urlParams.orcid_id) {
          // Success callback
          setUser({ 
            orcid_id: urlParams.orcid_id,
            name: urlParams.name || ''
          });
          // Clean up URL
          window.history.replaceState({}, document.title, window.location.pathname);
        } else if (urlParams.error) {
          // Error callback
          setError(urlParams.description || urlParams.error);
          // Clean up URL
          window.history.replaceState({}, document.title, window.location.pathname);
        } else {
          // Check current session
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        }
      } catch (err) {
        console.error('Auth check failed:', err);
        setError('Failed to check authentication status');
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const handleLogin = () => {
    setError(null);
    initiateOrcidAuth('/authenticate');
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
    } catch (err) {
      console.error('Logout failed:', err);
      setError('Failed to logout');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <h3 className="text-red-800 font-medium">Authentication Error</h3>
        <p className="text-red-600 mt-1">{error}</p>
        <button
          onClick={() => setError(null)}
          className="mt-2 px-3 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200"
        >
          Dismiss
        </button>
      </div>
    );
  }

  if (user) {
    return (
      <div className="p-4 bg-green-50 border border-green-200 rounded-md">
        <h3 className="text-green-800 font-medium">Successfully Authenticated</h3>
        <p className="text-green-600 mt-1">
          ORCID ID: <span className="font-mono">{user.orcid_id}</span>
        </p>
        {user.name && (
          <p className="text-green-600">
            Name: {user.name}
          </p>
        )}
        <button
          onClick={handleLogout}
          className="mt-3 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">ORCID Authentication</h2>
      <p className="text-gray-600 mb-4">
        Connect your ORCID account to access your researcher profile and publications.
      </p>
      <button
        onClick={handleLogin}
        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <span>Sign in with ORCID</span>
      </button>
    </div>
  );
};

export default OrcidAuth; 