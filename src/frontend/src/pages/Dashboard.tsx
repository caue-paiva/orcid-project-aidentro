
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
import { getCurrentUserIdentity, UserIdentity } from "@/api/orcidApi";
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
        const identity = await getCurrentUserIdentity();
        setUserIdentity(identity);
      } catch (error) {
        console.error("Failed to fetch user identity:", error);
        setUserError("Failed to load user profile");
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserIdentity();
  }, []);

  // Determine display name and authentication status
  const isAuthenticated = userIdentity?.authenticated || false;
  const displayName = isAuthenticated ? userIdentity.name : 'Guest';

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
                        onClick={() => {
                          console.log('Button clicked, opening modal');
                          console.log('userIdentity:', userIdentity);
                          console.log('isUserModalOpen before:', isUserModalOpen);
                          setIsUserModalOpen(true);
                        }}
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
              onClick={() => window.location.href = "/publications/import"}
            >
              <FilePlus className="h-4 w-4 mr-2" />
              Import Publications
            </Button>
            {isAuthenticated ? (
              <Button
                className="bg-orcid-green hover:bg-orcid-green/90"
                onClick={() => window.location.href = "/profile"}
              >
                View ORCID Profile
              </Button>
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
            <UserProfile />
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
