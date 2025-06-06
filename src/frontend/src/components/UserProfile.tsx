import React, { useState, useEffect } from 'react';
import { getCurrentUserIdentity, getUserIdentity, UserIdentity } from '../api/orcidApi';

interface UserProfileProps {
  orcidId?: string; // Optional: if provided, fetch specific user; otherwise get current user
}

const UserProfile: React.FC<UserProfileProps> = ({ orcidId }) => {
  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserIdentity = async () => {
      try {
        setLoading(true);
        setError(null);

        let identity: UserIdentity | null = null;

        if (orcidId) {
          // Fetch specific user by ORCID ID
          identity = await getUserIdentity(orcidId);
        } else {
          // Fetch current authenticated user
          identity = await getCurrentUserIdentity();
        }

        setUserIdentity(identity);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user profile');
      } finally {
        setLoading(false);
      }
    };

    fetchUserIdentity();
  }, [orcidId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading profile...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Profile</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!userIdentity) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-yellow-800 font-semibold mb-2">Profile Not Found</h3>
        <p className="text-yellow-600">
          {orcidId 
            ? 'No profile found for the provided ORCID ID.' 
            : 'No authenticated user found. Please sign in with ORCID.'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
      <div className="flex items-start space-x-4">
        {/* ORCID Logo/Icon */}
        <div className="flex-shrink-0">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-green-600" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
        </div>

        {/* User Information */}
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h2 className="text-xl font-semibold text-gray-900">{userIdentity.name}</h2>
            {userIdentity.authenticated && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Authenticated
              </span>
            )}
          </div>

          <div className="space-y-2 text-sm text-gray-600">
            {/* ORCID ID */}
            <div className="flex items-center space-x-2">
              <span className="font-medium">ORCID iD:</span>
              <a 
                href={userIdentity.profile_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                {userIdentity.orcid_id}
              </a>
            </div>

            {/* Email */}
            {userIdentity.email && (
              <div className="flex items-center space-x-2">
                <span className="font-medium">Email:</span>
                <span>{userIdentity.email}</span>
              </div>
            )}

            {/* Current Affiliation */}
            {userIdentity.current_affiliation && (
              <div className="flex items-center space-x-2">
                <span className="font-medium">Current Affiliation:</span>
                <span>{userIdentity.current_affiliation}</span>
              </div>
            )}

            {/* Location */}
            {userIdentity.current_location && (
              <div className="flex items-center space-x-2">
                <span className="font-medium">Location:</span>
                <span>{userIdentity.current_location}</span>
              </div>
            )}
          </div>

          {/* Session Info (if available) */}
          {userIdentity.session_data && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-medium text-blue-900 mb-2">Session Information</h4>
              <div className="text-xs text-blue-700 space-y-1">
                <div>Session ORCID ID: {userIdentity.session_data.session_orcid_id}</div>
                <div>Access Token Available: {userIdentity.session_data.access_token_available ? 'Yes' : 'No'}</div>
              </div>
            </div>
          )}

          {/* Profile Link */}
          <div className="mt-4">
            <a
              href={userIdentity.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              View ORCID Profile
              <svg className="ml-2 -mr-0.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile; 