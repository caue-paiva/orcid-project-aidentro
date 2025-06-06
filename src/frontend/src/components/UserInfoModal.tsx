import React from 'react';
import { X, ExternalLink, Mail, MapPin, Building } from 'lucide-react';
import { UserIdentity } from '../api/orcidApi';

interface UserInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  userIdentity: UserIdentity;
}

const UserInfoModal: React.FC<UserInfoModalProps> = ({ isOpen, onClose, userIdentity }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Background overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      ></div>
      
      {/* Modal content */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">ORCID Profile Summary</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* User Avatar/Icon */}
            <div className="text-center mb-6">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-10 h-10 text-green-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{userIdentity.name}</h3>
              {userIdentity.authenticated ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                  ✓ ORCID Verified
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mt-1">
                  Not Authenticated
                </span>
              )}
            </div>

            {/* User Details */}
            <div className="space-y-4">
              {/* ORCID ID */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <ExternalLink className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">ORCID iD</p>
                  {userIdentity.orcid_id !== 'Unknown' ? (
                    <a 
                      href={userIdentity.profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 underline break-all"
                    >
                      {userIdentity.orcid_id}
                    </a>
                  ) : (
                    <p className="text-sm text-gray-600 break-all">{userIdentity.orcid_id}</p>
                  )}
                </div>
              </div>

              {/* Email */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Mail className="w-4 h-4 text-purple-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">Email</p>
                  <p className="text-sm text-gray-600 break-all">{userIdentity.email || 'Unknown'}</p>
                </div>
              </div>

              {/* Current Affiliation */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Building className="w-4 h-4 text-orange-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">Current Affiliation</p>
                  <p className="text-sm text-gray-600">{userIdentity.current_affiliation || 'Unknown'}</p>
                </div>
              </div>

              {/* Location */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <MapPin className="w-4 h-4 text-green-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">Location</p>
                  <p className="text-sm text-gray-600">{userIdentity.current_location || 'Unknown'}</p>
                </div>
              </div>

              {/* Session Information */}
              {userIdentity.session_data && (
                <div className="bg-blue-50 rounded-lg p-4 mt-6">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">Session Details</h4>
                  <div className="text-xs text-blue-700 space-y-1">
                    <div className="flex justify-between">
                      <span>Session ORCID:</span>
                      <span className="font-mono">{userIdentity.session_data.session_orcid_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Access Token:</span>
                      <span className={userIdentity.session_data.access_token_available ? 'text-green-700' : 'text-red-700'}>
                        {userIdentity.session_data.access_token_available ? 'Available' : 'Not Available'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Close
            </button>
            <a
              href={userIdentity.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              View Full Profile
              <ExternalLink className="ml-2 h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserInfoModal;