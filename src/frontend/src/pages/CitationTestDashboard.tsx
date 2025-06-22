import { useEffect, useState } from "react";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import MetricsCard from "@/components/dashboard/MetricsCard";
import CitationChart from "@/components/dashboard/CitationChart";
import UserProfile from "@/components/UserProfile";
import { testCitationAnalysis, getCitationMetrics, getUserIdentity, UserIdentity } from "@/api/orcidApi";
import { CitationMetrics, CitationData } from "@/types";
import { Book, BookUser, Award, Users, RefreshCw, AlertCircle } from "lucide-react";

interface TestData {
  testOrcidId: string;
  userIdentity: UserIdentity;
  citationMetrics: CitationMetrics;
  citationAnalysis: any;
}

const CitationTestDashboard = () => {
  const [testData, setTestData] = useState<TestData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTestData = async () => {
    try {
      console.log("🔄 CitationTestDashboard: Starting fetchTestData");
      setLoading(true);
      setError(null);
      
      console.log("🔄 Fetching citation test data...");
      const data = await testCitationAnalysis(5);
      
      console.log("✅ Test data received:", data);
      console.log("📊 Citation metrics:", data.citationMetrics);
      console.log("📈 Citation chart data:", data.citationMetrics?.citationChartData);
      
      setTestData(data);
      console.log("✅ State updated with test data");
      
    } catch (err) {
      console.error("❌ Error fetching test data:", err);
      setError(err instanceof Error ? err.message : 'Failed to fetch citation data');
    } finally {
      setLoading(false);
      console.log("🏁 fetchTestData completed");
    }
  };

  // Auto-fetch on component mount
  useEffect(() => {
    console.log("🚀 CitationTestDashboard mounted, calling fetchTestData");
    fetchTestData();
  }, []);

  console.log("🎨 Rendering CitationTestDashboard - loading:", loading, "error:", error, "testData:", !!testData);

  // Log when we have test data
  if (testData) {
    console.log("🎯 Rendering success state with testData");
    console.log("🎨 About to render CitationChart with data:", testData.citationMetrics?.citation_chart_data);
  }

  return (
    <Layout>
      <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Citation Analysis Test Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Real citation data from ORCID & CrossRef APIs
            </p>
            {testData && (
              <p className="text-sm text-gray-500 mt-1">
                Test ORCID ID: <code className="bg-gray-100 px-2 py-1 rounded">{testData.testOrcidId}</code>
              </p>
            )}
          </div>
          <div className="mt-4 md:mt-0">
            <Button
              onClick={fetchTestData}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Loading...' : 'Refresh Data'}</span>
            </Button>
          </div>
        </div>

        {/* Debug Info (always visible in development) */}
        {process.env.NODE_ENV === 'development' && (
          <Card className="mb-4 border-blue-200 bg-blue-50">
            <CardContent className="p-4">
              <div className="text-sm">
                <div className="font-semibold text-blue-800">Debug Info:</div>
                <div>Loading: {loading ? 'true' : 'false'}</div>
                <div>Error: {error || 'none'}</div>
                <div>TestData: {testData ? 'loaded' : 'null'}</div>
                {testData && (
                  <div>
                    <div>Citations: {testData.citationMetrics?.total_citations || 'N/A'}</div>
                    <div>Chart Data Points: {testData.citationMetrics?.citation_chart_data?.length || 'N/A'}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {loading && (
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex items-center justify-center space-x-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orcid-green"></div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">Analyzing Citations...</p>
                  <p className="text-sm text-gray-600">
                    Fetching publications from ORCID and citation counts from CrossRef
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State */}
        {error && (
          <Card className="mb-8 border-red-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <AlertCircle className="h-6 w-6 text-red-500" />
                <div>
                  <h3 className="text-lg font-semibold text-red-800">Error Loading Citation Data</h3>
                  <p className="text-red-600 mt-1">{error}</p>
                  <p className="text-sm text-gray-600 mt-2">
                    This could be due to network issues, API rate limits, or missing DOIs in the ORCID record.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Success State */}
        {testData && (
          <>
            {/* User Profile Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Researcher Profile</h2>
              <UserProfile userIdentity={testData.userIdentity} />
            </div>

            {/* Metrics Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <MetricsCard
                title="Total Publications"
                value={testData.citationMetrics?.publications_count || 0}
                icon={<Book className="h-4 w-4 text-gray-500" />}
                description="Publications with DOIs"
              />
              <MetricsCard
                title="Total Citations"
                value={testData.citationMetrics?.total_citations || 0}
                icon={<BookUser className="h-4 w-4 text-gray-500" />}
                trend={testData.citationMetrics?.citation_trend}
                description="Real citation count from CrossRef"
              />
              <MetricsCard
                title="H-Index (Approx)"
                value={testData.citationMetrics?.h_index_approximation || 0}
                icon={<Award className="h-4 w-4 text-gray-500" />}
                description="Simplified h-index calculation"
              />
              <MetricsCard
                title="Cited Publications"
                value={testData.citationMetrics?.cited_publications_count || 0}
                icon={<Users className="h-4 w-4 text-gray-500" />}
                description={`${testData.citationMetrics?.cited_publications_count || 0}/${testData.citationMetrics?.publications_count || 0} publications cited`}
              />
            </div>

            {/* Citation Chart */}
            <div className="mb-8">
              <CitationChart
                citationData={testData.citationMetrics?.citation_chart_data}
                isLoading={false}
                error={testData.citationMetrics?.analysis_success ? undefined : "Analysis had issues"}
              />
            </div>

            {/* Analysis Details */}
            <div className="grid gap-4 md:grid-cols-2 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle>Analysis Summary</CardTitle>
                  <CardDescription>Details about the citation analysis process</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Analysis Period:</span>
                      <span className="font-semibold">{testData.citationAnalysis.analysis_period}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Successful API Lookups:</span>
                      <span className="font-semibold">
                        {testData.citationAnalysis.successful_lookups}/{testData.citationAnalysis.total_publications}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Average Citations/Year:</span>
                      <span className="font-semibold">{testData.citationMetrics?.avg_citations_per_year || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Analysis Status:</span>
                      <span className={`font-semibold ${testData.citationMetrics?.analysis_success ? 'text-green-600' : 'text-yellow-600'}`}>
                        {testData.citationMetrics?.analysis_success ? 'Success' : 'Partial'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Data Sources</CardTitle>
                  <CardDescription>Where this data comes from</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div>
                      <div className="font-semibold text-orcid-green">ORCID Public API</div>
                      <div className="text-gray-600">Publications, personal info, affiliations</div>
                    </div>
                    <div>
                      <div className="font-semibold text-blue-600">CrossRef API</div>
                      <div className="text-gray-600">Citation counts via DOI lookup</div>
                    </div>
                    <div>
                      <div className="font-semibold text-purple-600">Backend Integration</div>
                      <div className="text-gray-600">
                        Python integration layer processing {testData.citationAnalysis.total_publications} publications
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Raw Data Debug (Development Only) */}
            {process.env.NODE_ENV === 'development' && (
              <Card>
                <CardHeader>
                  <CardTitle>Debug: Raw API Response</CardTitle>
                  <CardDescription>Raw data from the backend API (development only)</CardDescription>
                </CardHeader>
                <CardContent>
                  <details>
                    <summary className="cursor-pointer text-sm font-semibold text-gray-700 hover:text-gray-900">
                      Click to view raw citation analysis data
                    </summary>
                    <pre className="mt-4 bg-gray-50 p-4 rounded-lg text-xs overflow-auto max-h-64">
                      {JSON.stringify(testData.citationAnalysis, null, 2)}
                    </pre>
                  </details>
                  <details className="mt-4">
                    <summary className="cursor-pointer text-sm font-semibold text-gray-700 hover:text-gray-900">
                      Click to view citation metrics data
                    </summary>
                    <pre className="mt-4 bg-gray-50 p-4 rounded-lg text-xs overflow-auto max-h-64">
                      {JSON.stringify(testData.citationMetrics, null, 2)}
                    </pre>
                  </details>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Help Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>About This Test Dashboard</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <p>
                This test dashboard demonstrates the citation analysis functionality by:
              </p>
              <ul className="mt-2">
                <li>Fetching publications from a researcher's ORCID record</li>
                <li>Extracting DOIs from the publications</li>
                <li>Looking up citation counts for each DOI using the CrossRef API</li>
                <li>Aggregating citation data by year and calculating metrics</li>
                <li>Displaying the data in interactive charts and cards</li>
              </ul>
              <p className="mt-4">
                The hardcoded test ORCID ID <code>{testData?.testOrcidId || '0000-0003-1574-0784'}</code> is used 
                for consistent testing. In production, this would use the authenticated user's ORCID ID.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default CitationTestDashboard; 