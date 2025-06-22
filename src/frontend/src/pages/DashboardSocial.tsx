import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import MetricsCard from "@/components/dashboard/MetricsCard";
import CitationChart from "@/components/dashboard/CitationChart";
import UserProfile from "@/components/UserProfile";
import { getUserIdentity, UserIdentity, getCitationMetrics } from "@/api/orcidApi";
import { CitationMetrics } from "@/types";
import { Book, BookUser, Award, Users, RefreshCw, ArrowLeft, ExternalLink, User } from "lucide-react";
import { toast } from "sonner";

const DashboardSocial = () => {
  const [searchParams] = useSearchParams();
  const orcidId = searchParams.get('orcid_id');
  const displayName = searchParams.get('name');
  const institution = searchParams.get('institution');

  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [userError, setUserError] = useState<string | null>(null);
  
  // Citation analysis state
  const [citationMetrics, setCitationMetrics] = useState<CitationMetrics | null>(null);
  const [loadingCitations, setLoadingCitations] = useState(false);
  const [citationError, setCitationError] = useState<string | null>(null);

  // Validate required parameters
  useEffect(() => {
    if (!orcidId) {
      setUserError("ORCID ID is required");
      setLoadingUser(false);
      return;
    }

    // Show success message with researcher info
    if (displayName) {
      toast.success(`Viewing ${displayName}'s research profile`);
    }
  }, [orcidId, displayName]);

  // Fetch user identity
  useEffect(() => {
    const fetchUserIdentity = async () => {
      if (!orcidId) return;

      try {
        setLoadingUser(true);
        setUserError(null);
        
        console.log('Fetching user identity for ORCID ID:', orcidId);
        const identity = await getUserIdentity(orcidId);
        setUserIdentity(identity);
        
        // Auto-fetch citation data
        fetchCitationData(orcidId);
      } catch (error) {
        console.error("Failed to fetch user identity:", error);
        setUserError("Failed to load researcher profile");
        toast.error("Failed to load researcher profile");
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserIdentity();
  }, [orcidId]);

  // Fetch citation analysis data
  const fetchCitationData = async (targetOrcidId?: string) => {
    try {
      setLoadingCitations(true);
      setCitationError(null);
      
      const orcidToUse = targetOrcidId || orcidId;
      if (!orcidToUse) {
        throw new Error("No ORCID ID available for citation analysis");
      }
      
      console.log("🔄 Fetching citation metrics for:", orcidToUse);
      const metrics = await getCitationMetrics(orcidToUse);
      console.log("✅ Citation metrics received:", metrics);
      
      setCitationMetrics(metrics);
    } catch (error) {
      console.error("❌ Error fetching citation data:", error);
      setCitationError(error instanceof Error ? error.message : 'Failed to fetch citation data');
    } finally {
      setLoadingCitations(false);
    }
  };

  // Function to refresh citation data
  const handleRefreshCitations = () => {
    if (orcidId) {
      fetchCitationData(orcidId);
    }
  };

  // Get display information - prioritize query params, fall back to API data
  const getDisplayName = () => {
    if (displayName) return displayName;
    if (userIdentity?.name) return userIdentity.name;
    return 'Researcher';
  };

  const getDisplayInstitution = () => {
    if (institution) return institution;
    if (userIdentity?.current_affiliation) return userIdentity.current_affiliation;
    return null;
  };

  // Error state - missing ORCID ID
  if (!orcidId) {
    return (
      <Layout>
        <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">
              <User className="h-16 w-16 mx-auto" />
            </div>
            <h2 className="text-xl font-semibold mb-2 text-red-800">
              Missing ORCID ID
            </h2>
            <p className="text-gray-600 max-w-md mx-auto mb-4">
              This page requires an ORCID ID to display researcher information.
            </p>
            <Link to="/search">
              <Button className="bg-orcid-green hover:bg-orcid-green/90">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Search
              </Button>
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Link to="/search">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Search
                </Button>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Researcher Profile</h1>
            </div>
            
            <div className="mt-1 space-y-1">
              {loadingUser ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <p className="text-gray-600">Loading profile...</p>
                </div>
              ) : userError ? (
                <div className="space-y-1">
                  <p className="text-gray-600">{getDisplayName()}</p>
                  <p className="text-sm text-red-500">{userError}</p>
                  <p className="text-sm text-gray-500">ORCID ID: {orcidId}</p>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <p className="text-gray-600 text-lg font-medium">
                      {getDisplayName()}
                    </p>
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      <User className="w-3 h-3 mr-1" />
                      Public Profile
                    </span>
                  </div>
                  
                  {getDisplayInstitution() && (
                    <p className="text-sm text-gray-500">
                      {getDisplayInstitution()}
                      {userIdentity?.current_location && ` • ${userIdentity.current_location}`}
                    </p>
                  )}
                  
                  <p className="text-sm text-gray-500">
                    ORCID ID: {orcidId}
                  </p>
                </div>
              )}
            </div>
          </div>
          
          <div className="mt-4 md:mt-0 flex gap-2">
            <Button
              variant="outline"
              onClick={handleRefreshCitations}
              disabled={loadingCitations}
              className="flex items-center"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loadingCitations ? 'animate-spin' : ''}`} />
              {loadingCitations ? 'Loading...' : 'Refresh Citations'}
            </Button>
            
            {userIdentity?.profile_url && (
              <Button
                className="bg-orcid-green hover:bg-orcid-green/90"
                onClick={() => window.open(userIdentity.profile_url, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View ORCID Profile
              </Button>
            )}
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricsCard
            title="Total Publications"
            value={citationMetrics?.publications_count || 0}
            icon={<Book className="h-4 w-4 text-gray-500" />}
            description="Publications with DOIs from ORCID"
          />
          <MetricsCard
            title="Citations"
            value={citationMetrics?.total_citations || 0}
            icon={<BookUser className="h-4 w-4 text-gray-500" />}
            trend={citationMetrics?.citation_trend}
            description="Citation count from CrossRef"
          />
          <MetricsCard
            title="h-index"
            value={citationMetrics?.h_index_approximation || 0}
            icon={<Award className="h-4 w-4 text-gray-500" />}
            description="Approximated h-index"
          />
          <MetricsCard
            title="Cited Publications"
            value={citationMetrics?.cited_publications_count || 0}
            icon={<Users className="h-4 w-4 text-gray-500" />}
            description={citationMetrics 
              ? `${citationMetrics.cited_publications_count}/${citationMetrics.publications_count} publications cited`
              : "Publications that have been cited"}
          />
        </div>

        {/* Loading state for citation analysis */}
        {loadingCitations && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orcid-green"></div>
              <div>
                <h3 className="text-lg font-semibold text-blue-900">
                  Analyzing Citations...
                </h3>
                <p className="text-blue-700 text-sm">
                  Fetching publications from ORCID and citation counts from CrossRef
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Citation error state */}
        {citationError && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <div className="text-red-500">⚠️</div>
              <div>
                <h3 className="text-lg font-semibold text-red-800">Citation Analysis Error</h3>
                <p className="text-red-600 text-sm">{citationError}</p>
                <p className="text-gray-600 text-sm mt-1">
                  This could be due to network issues, API rate limits, or missing DOIs in the ORCID record.
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
              citationData={citationMetrics?.citation_chart_data}
              isLoading={loadingCitations}
              error={citationError || undefined}
            />
          </div>
          
          <div className="space-y-4">
            {/* Researcher Info Card */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center">
                <User className="h-4 w-4 mr-2 text-orcid-green" />
                Researcher Information
              </h3>
              <div className="space-y-2 text-sm">
                <div className="bg-white p-3 rounded-lg border border-gray-100">
                  <div className="font-medium text-gray-800">{getDisplayName()}</div>
                  {getDisplayInstitution() && (
                    <div className="text-gray-600 text-xs mt-1">{getDisplayInstitution()}</div>
                  )}
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-gray-100">
                  <div className="text-gray-600 text-xs">ORCID ID</div>
                  <div className="font-mono text-xs text-gray-800">{orcidId}</div>
                </div>
                
                {userIdentity?.current_location && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100">
                    <div className="text-gray-600 text-xs">Location</div>
                    <div className="text-gray-800">{userIdentity.current_location}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3">Actions</h3>
              <div className="space-y-2 text-sm">
                {userIdentity?.profile_url && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                    <a 
                      href={userIdentity.profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-800 hover:text-orcid-green flex items-center justify-between w-full"
                    >
                      <span>View full ORCID profile</span>
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                )}
                
                <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <Link 
                    to="/search" 
                    className="text-gray-800 hover:text-orcid-green flex items-center justify-between w-full"
                  >
                    <span>Search for more researchers</span>
                    <ArrowLeft className="h-4 w-4" />
                  </Link>
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <Link 
                    to="/dashboard" 
                    className="text-gray-800 hover:text-orcid-green flex items-center justify-between w-full"
                  >
                    <span>View your own dashboard</span>
                    <User className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Info (Development Only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed bottom-4 left-4 bg-black text-white p-2 text-xs rounded max-w-sm">
            <div>ORCID: {orcidId || 'null'}</div>
            <div>Name: {displayName || 'null'}</div>
            <div>Institution: {institution || 'null'}</div>
            <div>User: {userIdentity ? 'loaded' : 'null'}</div>
            <div>Citations: {citationMetrics ? 'loaded' : 'null'}</div>
            <div>Loading: {loadingCitations ? 'true' : 'false'}</div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default DashboardSocial; 