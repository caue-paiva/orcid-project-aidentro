import { Link } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import MetricsCard from "@/components/dashboard/MetricsCard";
import ProfileCompletion from "@/components/dashboard/ProfileCompletion";
import RecentPublications from "@/components/dashboard/RecentPublications";
import CitationChart from "@/components/dashboard/CitationChart";
import SocialMediaCard from "@/components/dashboard/SocialMediaCard";
import AddSocialMediaModal from "@/components/dashboard/AddSocialMediaModal";
import UserProfile from "@/components/UserProfile";
import UserInfoModal from "@/components/UserInfoModal";
import { getCurrentUserIdentity, getUserIdentity, UserIdentity, getCitationMetrics, getResearcherPapers, ResearcherPapersResponse, getSocialMediaAccounts, SocialMediaResponse, addSocialMediaAccount } from "@/api/orcidApi";
import { getStoredOrcidId, isOrcidAuthenticated, clearOrcidAuth } from "@/utils/orcidAuth";
import { CitationMetrics } from "@/types";
import { Book, FilePlus, Users, Award, BookUser, Lightbulb, User, RefreshCw, Plus } from "lucide-react";
import { useEffect, useState } from "react";

// Demo ORCID ID for fallback data
const DEMO_ORCID_ID = "0000-0003-1574-0784";

const Dashboard = () => {
  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [userError, setUserError] = useState<string | null>(null);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  
  // Citation analysis state
  const [citationMetrics, setCitationMetrics] = useState<CitationMetrics | null>(null);
  const [loadingCitations, setLoadingCitations] = useState(false);
  const [citationError, setCitationError] = useState<string | null>(null);

  // Demo/fallback citation data state
  const [demoCitationMetrics, setDemoCitationMetrics] = useState<CitationMetrics | null>(null);
  const [loadingDemoData, setLoadingDemoData] = useState(false);

  // Papers state
  const [papers, setPapers] = useState<ResearcherPapersResponse | null>(null);
  const [loadingPapers, setLoadingPapers] = useState(false);
  const [papersError, setPapersError] = useState<string | null>(null);
  
  // Demo papers state
  const [demoPapers, setDemoPapers] = useState<ResearcherPapersResponse | null>(null);
  const [loadingDemoPapers, setLoadingDemoPapers] = useState(false);

  // Social media state
  const [socialMedia, setSocialMedia] = useState<SocialMediaResponse | null>(null);
  const [loadingSocialMedia, setLoadingSocialMedia] = useState(false);
  const [socialMediaError, setSocialMediaError] = useState<string | null>(null);
  
  // Demo social media state
  const [demoSocialMedia, setDemoSocialMedia] = useState<SocialMediaResponse | null>(null);
  const [loadingDemoSocialMedia, setLoadingDemoSocialMedia] = useState(false);

  // Modal states
  const [showAddSocialMediaModal, setShowAddSocialMediaModal] = useState(false);
  const [addingSocialMedia, setAddingSocialMedia] = useState(false);

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
          
          // Auto-fetch citation data, papers, and social media for authenticated users
          fetchCitationData(storedOrcidId);
          fetchPapers(storedOrcidId);
          fetchSocialMedia(storedOrcidId);
        } else {
          console.log('No stored ORCID ID found, loading demo data');
          setUserIdentity(null);
          
          // Fetch demo citation data, papers, and social media for non-authenticated users
          fetchDemoCitationData();
          fetchDemoPapers();
          fetchDemoSocialMedia();
        }
      } catch (error) {
        console.error("Failed to fetch user identity:", error);
        setUserError("Failed to load user profile");
        // Clear invalid stored auth on error
        clearOrcidAuth();
        // Still try to load demo data
        fetchDemoCitationData();
        fetchDemoPapers();
        fetchDemoSocialMedia();
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserIdentity();
  }, []);

  // Fetch citation analysis data for authenticated user
  const fetchCitationData = async (orcidId?: string) => {
    try {
      setLoadingCitations(true);
      setCitationError(null);
      
      const targetOrcidId = orcidId || getStoredOrcidId();
      if (!targetOrcidId) {
        throw new Error("No ORCID ID available for citation analysis");
      }
      
      console.log("🔄 Fetching citation metrics for:", targetOrcidId);
      const metrics = await getCitationMetrics(targetOrcidId);
      console.log("✅ Citation metrics received:", metrics);
      
      setCitationMetrics(metrics);
    } catch (error) {
      console.error("❌ Error fetching citation data:", error);
      setCitationError(error instanceof Error ? error.message : 'Failed to fetch citation data');
    } finally {
      setLoadingCitations(false);
    }
  };

  // Fetch demo citation data from the demo ORCID ID
  const fetchDemoCitationData = async () => {
    try {
      setLoadingDemoData(true);
      
      console.log("🔄 Fetching demo citation metrics for:", DEMO_ORCID_ID);
      const metrics = await getCitationMetrics(DEMO_ORCID_ID);
      console.log("✅ Demo citation metrics received:", metrics);
      
      setDemoCitationMetrics(metrics);
    } catch (error) {
      console.error("❌ Error fetching demo citation data:", error);
      // On error, we'll just show empty data
      setDemoCitationMetrics(null);
    } finally {
      setLoadingDemoData(false);
    }
  };

  // Fetch papers for authenticated user
  const fetchPapers = async (orcidId?: string) => {
    try {
      setLoadingPapers(true);
      setPapersError(null);
      
      const targetOrcidId = orcidId || getStoredOrcidId();
      if (!targetOrcidId) {
        throw new Error("No ORCID ID available for fetching papers");
      }
      
      console.log("📄 Fetching papers for:", targetOrcidId);
      const papersData = await getResearcherPapers(targetOrcidId, 10);
      console.log("✅ Papers received:", papersData);
      
      setPapers(papersData);
    } catch (error) {
      console.error("❌ Error fetching papers:", error);
      setPapersError(error instanceof Error ? error.message : 'Failed to fetch papers');
    } finally {
      setLoadingPapers(false);
    }
  };

  // Fetch demo papers from the demo ORCID ID
  const fetchDemoPapers = async () => {
    try {
      setLoadingDemoPapers(true);
      
      console.log("📄 Fetching demo papers for:", DEMO_ORCID_ID);
      const papersData = await getResearcherPapers(DEMO_ORCID_ID, 10);
      console.log("✅ Demo papers received:", papersData);
      
      setDemoPapers(papersData);
    } catch (error) {
      console.error("❌ Error fetching demo papers:", error);
      // On error, we'll just show empty data
      setDemoPapers(null);
    } finally {
      setLoadingDemoPapers(false);
    }
  };

  // Fetch social media for authenticated user
  const fetchSocialMedia = async (orcidId?: string) => {
    try {
      setLoadingSocialMedia(true);
      setSocialMediaError(null);
      
      const targetOrcidId = orcidId || getStoredOrcidId();
      if (!targetOrcidId) {
        throw new Error("No ORCID ID available for fetching social media");
      }
      
      console.log("📱 Fetching social media for:", targetOrcidId);
      const socialMediaData = await getSocialMediaAccounts(targetOrcidId);
      console.log("✅ Social media received:", socialMediaData);
      
      setSocialMedia(socialMediaData);
    } catch (error) {
      console.error("❌ Error fetching social media:", error);
      setSocialMediaError(error instanceof Error ? error.message : 'Failed to fetch social media');
    } finally {
      setLoadingSocialMedia(false);
    }
  };

  // Fetch demo social media from the demo ORCID ID
  const fetchDemoSocialMedia = async () => {
    try {
      setLoadingDemoSocialMedia(true);
      
      console.log("📱 Fetching demo social media for:", DEMO_ORCID_ID);
      const socialMediaData = await getSocialMediaAccounts(DEMO_ORCID_ID);
      console.log("✅ Demo social media received:", socialMediaData);
      
      setDemoSocialMedia(socialMediaData);
    } catch (error) {
      console.error("❌ Error fetching demo social media:", error);
      // On error, we'll just show empty data
      setDemoSocialMedia(null);
    } finally {
      setLoadingDemoSocialMedia(false);
    }
  };

  // Determine display name and authentication status
  const isAuthenticated = userIdentity?.authenticated || false;
  const displayName = isAuthenticated ? userIdentity.name : 'Guest';

  // Get the appropriate citation metrics, papers, and social media to display
  const displayMetrics = isAuthenticated ? citationMetrics : demoCitationMetrics;
  const isLoadingMetrics = isAuthenticated ? loadingCitations : loadingDemoData;
  
  const displayPapers = isAuthenticated ? papers : demoPapers;
  const isLoadingPapersDisplay = isAuthenticated ? loadingPapers : loadingDemoPapers;
  
  const displaySocialMedia = isAuthenticated ? socialMedia : demoSocialMedia;
  const isLoadingSocialMediaDisplay = isAuthenticated ? loadingSocialMedia : loadingDemoSocialMedia;

  // Logout function
  const handleLogout = () => {
    clearOrcidAuth();
    setUserIdentity(null);
    setCitationMetrics(null);
    setPapers(null);
    setPapersError(null);
    setSocialMedia(null);
    setSocialMediaError(null);
    // Load demo data again
    fetchDemoCitationData();
    fetchDemoPapers();
    fetchDemoSocialMedia();
    // Optionally redirect or refresh
    window.location.reload();
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

  // Function to refresh citation data, papers, and social media
  const handleRefreshCitations = () => {
    const storedOrcidId = getStoredOrcidId();
    if (storedOrcidId) {
      fetchCitationData(storedOrcidId);
      fetchPapers(storedOrcidId);
      fetchSocialMedia(storedOrcidId);
    } else {
      fetchDemoCitationData();
      fetchDemoPapers();
      fetchDemoSocialMedia();
    }
  };

  // Handle adding social media account
  const handleAddSocialMedia = () => {
    setShowAddSocialMediaModal(true);
  };

  // Handle submitting new social media account
  const handleSubmitSocialMedia = async (platform: string, username: string) => {
    const storedOrcidId = getStoredOrcidId();
    const targetOrcidId = storedOrcidId || DEMO_ORCID_ID;
    const isAuthenticatedUser = !!storedOrcidId;

    setAddingSocialMedia(true);
    try {
      await addSocialMediaAccount(targetOrcidId, platform, username);
      
      // Refresh social media data to show the new account
      if (isAuthenticatedUser) {
        await fetchSocialMedia(targetOrcidId);
      } else {
        await fetchDemoSocialMedia();
      }
      
      console.log(`✅ Social media account added successfully for ${isAuthenticatedUser ? 'authenticated user' : 'demo user'}`);
    } catch (error) {
      console.error("❌ Error adding social media account:", error);
      throw error; // Re-throw to let the modal handle the error display
    } finally {
      setAddingSocialMedia(false);
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
                <div className="space-y-1">
                  <p className="text-gray-600">Welcome, Guest</p>
                  <p className="text-sm text-gray-500">
                    Viewing demo data from ORCID researcher • Connect your ORCID for personal metrics
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <p className="text-gray-600">
                      Welcome back, {displayName.split(" ")[0]}
                    </p>
                    {isAuthenticated ? (
                      <button
                        onClick={handleOpenUserModal}
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors cursor-pointer"
                      >
                        <User className="w-3 h-3 mr-1" />
                        ORCID Verified
                      </button>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Demo Mode
                      </span>
                    )}
                  </div>
                  {isAuthenticated && userIdentity?.current_affiliation && (
                    <p className="text-sm text-gray-500">
                      {userIdentity.current_affiliation}
                      {userIdentity.current_location && ` • ${userIdentity.current_location}`}
                    </p>
                  )}
                  {!isAuthenticated && (
                    <p className="text-sm text-gray-500">
                      Viewing demo data from ORCID researcher {DEMO_ORCID_ID} • Connect your ORCID for personal metrics
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex gap-2">
            <Button
              variant="outline"
              onClick={handleRefreshCitations}
              disabled={isLoadingMetrics}
              className="flex items-center"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingMetrics ? 'animate-spin' : ''}`} />
              {isLoadingMetrics ? 'Loading...' : 'Refresh Citations'}
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

        {/* Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricsCard
            title="Total Publications"
            value={displayMetrics?.publications_count || 0}
            icon={<Book className="h-4 w-4 text-gray-500" />}
            description={isAuthenticated ? "Publications with DOIs from ORCID" : `Demo data from ORCID researcher`}
          />
          <MetricsCard
            title="Citations"
            value={displayMetrics?.total_citations || 0}
            icon={<BookUser className="h-4 w-4 text-gray-500" />}
            trend={displayMetrics?.citation_trend}
            description={isAuthenticated ? "Real citation count from CrossRef" : "Demo citation data from CrossRef"}
          />
          <MetricsCard
            title="h-index"
            value={displayMetrics?.h_index_approximation || 0}
            icon={<Award className="h-4 w-4 text-gray-500" />}
            description={isAuthenticated ? "Approximated h-index" : "Demo h-index calculation"}
          />
          <MetricsCard
            title={isAuthenticated ? "Cited Publications" : "Cited Publications"}
            value={displayMetrics?.cited_publications_count || 0}
            icon={<Users className="h-4 w-4 text-gray-500" />}
            description={displayMetrics 
              ? `${displayMetrics.cited_publications_count}/${displayMetrics.publications_count} publications cited`
              : "Publications that have been cited"}
          />
        </div>

        {/* Loading state for citation analysis */}
        {isLoadingMetrics && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orcid-green"></div>
              <div>
                <h3 className="text-lg font-semibold text-blue-900">
                  {isAuthenticated ? "Analyzing Your Citations..." : "Loading Demo Citation Data..."}
                </h3>
                <p className="text-blue-700 text-sm">
                  Fetching publications from ORCID and citation counts from CrossRef
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Citation error state */}
        {isAuthenticated && citationError && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <div className="text-red-500">⚠️</div>
              <div>
                <h3 className="text-lg font-semibold text-red-800">Citation Analysis Error</h3>
                <p className="text-red-600 text-sm">{citationError}</p>
                <p className="text-gray-600 text-sm mt-1">
                  This could be due to network issues, API rate limits, or missing DOIs in your ORCID record.
                </p>
              </div>
            </div>
          </div>
        )}

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
            <CitationChart
              citationData={displayMetrics?.citation_chart_data}
              isLoading={isLoadingMetrics}
              error={isAuthenticated ? (citationError || undefined) : undefined}
            />
            
            {/* Recent Publications */}
            <RecentPublications 
              publications={[]} 
              papers={displayPapers?.papers || []}
              isLoading={isLoadingPapersDisplay}
            />
          </div>
          
          <div className="space-y-4">
            {/* Profile Completion Widget - Only show when authenticated */}
            {isAuthenticated && userIdentity && (
              <ProfileCompletion researcher={{
                id: userIdentity.orcid_id,
                orcidId: userIdentity.orcid_id,
                name: userIdentity.name,
                institutionName: userIdentity.current_affiliation || "",
                countryCode: "",
                country: userIdentity.current_location || "",
                areaOfExpertise: [],
                metrics: {
                  publications: displayMetrics?.publications_count || 0,
                  citations: displayMetrics?.total_citations || 0,
                  hIndex: displayMetrics?.h_index_approximation || 0
                },
                followers: 0,
                following: 0,
                isCompleteProfile: false,
                onboardingStep: 0
              }} />
            )}

            {/* Social Media Card */}
            <SocialMediaCard
              socialMediaAccounts={displaySocialMedia?.social_media_accounts || []}
              isLoading={isLoadingSocialMediaDisplay}
              error={isAuthenticated ? (socialMediaError || undefined) : undefined}
              isAuthenticated={isAuthenticated}
              onAddAccount={handleAddSocialMedia}
            />


            
            {/* Suggested Actions */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center">
                <Lightbulb className="h-4 w-4 mr-2 text-orcid-green" />
                {isAuthenticated ? "Suggested Actions" : "Get Started"}
              </h3>
              <ul className="space-y-2 text-sm">
                {!isAuthenticated && (
                  <li className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                    <button 
                      onClick={() => window.location.href = "/orcid-test"}
                      className="text-gray-800 hover:text-orcid-green w-full text-left font-medium"
                    >
                      Connect your ORCID to see your personal citation metrics
                    </button>
                  </li>
                )}
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
                {isAuthenticated && !loadingCitations && !citationMetrics && (
                  <li className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                    <button 
                      onClick={handleRefreshCitations}
                      className="text-gray-800 hover:text-orcid-green w-full text-left"
                    >
                      Analyze your citation metrics
                    </button>
                  </li>
                )}
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

        {/* Add Social Media Modal */}
        <AddSocialMediaModal
          isOpen={showAddSocialMediaModal}
          onClose={() => setShowAddSocialMediaModal(false)}
          onSubmit={handleSubmitSocialMedia}
          isLoading={addingSocialMedia}
        />

      </div>
    </Layout>
  );
};

export default Dashboard;
