
import { Link } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import MetricsCard from "@/components/dashboard/MetricsCard";
import ProfileCompletion from "@/components/dashboard/ProfileCompletion";
import RecentPublications from "@/components/dashboard/RecentPublications";
import CitationChart from "@/components/dashboard/CitationChart";
import UserProfile from "@/components/UserProfile";
import UserInfoModal from "@/components/UserInfoModal";
import { currentUser, getPublicationsByResearcherId } from "@/data/mockData";
import { getCurrentUserIdentity, getUserIdentity, UserIdentity, debugSession, healthCheck } from "@/api/orcidApi";
import { getStoredOrcidId, isOrcidAuthenticated, clearOrcidAuth } from "@/utils/orcidAuth";
import { Book, FilePlus, Users, Award, BookUser, Lightbulb, User } from "lucide-react";
import { useEffect, useState } from "react";

const Dashboard = () => {
  const publications = getPublicationsByResearcherId(currentUser.id);
  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [userError, setUserError] = useState<string | null>(null);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);

  // Fetch current user's ORCID identity
  useEffect(() => {
    const fetchUserIdentity = async () => {
      try {
        setLoadingUser(true);
        setUserError(null);
        
        // Check if we have stored ORCID ID
        const storedOrcidId = getStoredOrcidId();
        const isAuthenticated = isOrcidAuthenticated();
        
        if (storedOrcidId && isAuthenticated) {
          console.log('Using stored ORCID ID:', storedOrcidId);
          // Use stored ORCID ID to get user identity
          const identity = await getUserIdentity(storedOrcidId);
          identity.authenticated = true; // Mark as authenticated since we have stored credentials
          setUserIdentity(identity);
        } else {
          console.log('No stored ORCID ID found');
          setUserIdentity(null);
        }
      } catch (error) {
        console.error("Failed to fetch user identity:", error);
        setUserError("Failed to load user profile");
        // Clear invalid stored auth on error
        clearOrcidAuth();
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserIdentity();
  }, []);

  // Determine display name and authentication status
  const isAuthenticated = userIdentity?.authenticated || false;
  const displayName = isAuthenticated ? userIdentity.name : 'Guest';

  // Logout function
  const handleLogout = () => {
    clearOrcidAuth();
    setUserIdentity(null);
    // Optionally redirect or refresh
    window.location.reload();
  };

  // Health check function
  const handleHealthCheck = async () => {
    try {
      const healthData = await healthCheck();
      console.log('Health Check Data:', healthData);
      alert(JSON.stringify(healthData, null, 2));
    } catch (error) {
      console.error('Health check failed:', error);
      alert('Health check failed: ' + error);
    }
  };

  // Debug function to check session
  const handleDebugSession = async () => {
    try {
      const sessionData = await debugSession();
      console.log('Session Debug Data:', sessionData);
      alert(JSON.stringify(sessionData, null, 2));
    } catch (error) {
      console.error('Debug session failed:', error);
      alert('Debug session failed: ' + error);
    }
  };

  // Function to handle user modal opening
  const handleOpenUserModal = async () => {
    try {
      // Always fetch fresh user identity when opening modal
      const storedOrcidId = getStoredOrcidId();
      if (storedOrcidId) {
        const identity = await getUserIdentity(storedOrcidId);
        identity.authenticated = true;
        setUserIdentity(identity);
      }
      setIsUserModalOpen(true);
    } catch (error) {
      console.error('Failed to refresh user identity:', error);
      setIsUserModalOpen(true); // Open modal anyway with existing data
    }
  };

  return (
    <Layout>
      <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <div className="mt-1 flex items-center space-x-2">
              {loadingUser ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <p className="text-gray-600">Loading profile...</p>
                </div>
              ) : userError ? (
                <p className="text-gray-600">
                  Welcome, Guest
                </p>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <p className="text-gray-600">
                      Welcome back, {displayName.split(" ")[0]}
                    </p>
                    {isAuthenticated && (
                      <button
                        onClick={handleOpenUserModal}
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors cursor-pointer"
                      >
                        <User className="w-3 h-3 mr-1" />
                        ORCID Verified
                      </button>
                    )}
                  </div>
                  {userIdentity?.current_affiliation && (
                    <p className="text-sm text-gray-500">
                      {userIdentity.current_affiliation}
                      {userIdentity.current_location && ` • ${userIdentity.current_location}`}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex gap-2">
            <Button
              variant="outline"
              className="flex items-center"
              onClick={handleHealthCheck}
            >
              Health Check
            </Button>
            <Button
              variant="outline"
              className="flex items-center"
              onClick={handleDebugSession}
            >
              Debug Session
            </Button>
            <Button
              variant="outline"
              className="flex items-center"
              onClick={() => window.location.href = "/publications/import"}
            >
              <FilePlus className="h-4 w-4 mr-2" />
              Import Publications
            </Button>
            {isAuthenticated ? (
              <div className="flex gap-2">
                <Button
                  className="bg-orcid-green hover:bg-orcid-green/90"
                  onClick={() => window.open(userIdentity?.profile_url, '_blank')}
                >
                  View ORCID Profile
                </Button>
                <Button
                  variant="outline"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </div>
            ) : (
              <Button
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => window.location.href = "/orcid-test"}
              >
                Connect ORCID
              </Button>
            )}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricsCard
            title="Total Publications"
            value={currentUser.metrics.publications}
            icon={<Book className="h-4 w-4 text-gray-500" />}
            trend={{ value: 12, isPositive: true }}
            description={isAuthenticated ? "Data from ORCID" : "Mock data"}
          />
          <MetricsCard
            title="Citations"
            value={currentUser.metrics.citations}
            icon={<BookUser className="h-4 w-4 text-gray-500" />}
            trend={{ value: 23, isPositive: true }}
            description={isAuthenticated ? "Data from ORCID" : "Mock data"}
          />
          <MetricsCard
            title="h-index"
            value={currentUser.metrics.hIndex}
            icon={<Award className="h-4 w-4 text-gray-500" />}
            trend={{ value: 2, isPositive: true }}
            description={isAuthenticated ? "Data from ORCID" : "Mock data"}
          />
          <MetricsCard
            title={isAuthenticated ? "ORCID Profile" : "Network"}
            value={isAuthenticated ? 1 : currentUser.followers + currentUser.following}
            icon={<Users className="h-4 w-4 text-gray-500" />}
            description={isAuthenticated 
              ? `ORCID ID: ${userIdentity?.orcid_id || 'N/A'}` 
              : `${currentUser.followers} followers, ${currentUser.following} following`}
          />
        </div>

        {/* ORCID User Profile Section */}
        {userIdentity && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">ORCID Profile</h2>
            <UserProfile userIdentity={userIdentity} />
          </div>
        )}

        <div className="mt-8 grid gap-4 grid-cols-1 lg:grid-cols-4">
          <div className="lg:col-span-3 space-y-4">
            {/* Citation Chart */}
            <CitationChart baseCitations={currentUser.metrics.citations / 5} />
            
            {/* Recent Publications */}
            <RecentPublications publications={publications} />
          </div>
          
          <div className="space-y-4">
            {/* Profile Completion Widget */}
            <ProfileCompletion researcher={currentUser} />
            
            {/* Suggested Actions */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center">
                <Lightbulb className="h-4 w-4 mr-2 text-orcid-green" />
                Suggested Actions
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <Link to="/publications/import" className="text-gray-800 hover:text-orcid-green">
                    Import your latest publications from Google Scholar
                  </Link>
                </li>
                <li className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <Link to="/dashboard/network" className="text-gray-800 hover:text-orcid-green">
                    Connect with researchers in your field
                  </Link>
                </li>
                <li className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <Link to="/profile/edit" className="text-gray-800 hover:text-orcid-green">
                    Add social media links to your profile
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* User Info Modal */}
        {isUserModalOpen && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div 
              className="fixed inset-0 bg-black bg-opacity-50"
              onClick={() => {
                console.log('Overlay clicked, closing modal');
                setIsUserModalOpen(false);
              }}
            ></div>
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h2 className="text-xl font-bold mb-4">Test Modal</h2>
                <p>Modal is working! This is a test.</p>
                <div className="mt-4">
                  <button
                    onClick={() => setIsUserModalOpen(false)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Close
                  </button>
                </div>
                {userIdentity && (
                  <div className="mt-4 text-sm">
                    <p><strong>Name:</strong> {userIdentity.name}</p>
                    <p><strong>ORCID:</strong> {userIdentity.orcid_id}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed bottom-4 left-4 bg-black text-white p-2 text-xs rounded">
            Modal Open: {isUserModalOpen ? 'true' : 'false'} | 
            User: {userIdentity ? 'exists' : 'null'} | 
            Auth: {isAuthenticated ? 'true' : 'false'}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;
