
import { Link } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import MetricsCard from "@/components/dashboard/MetricsCard";
import ProfileCompletion from "@/components/dashboard/ProfileCompletion";
import RecentPublications from "@/components/dashboard/RecentPublications";
import CitationChart from "@/components/dashboard/CitationChart";
import { currentUser, getPublicationsByResearcherId } from "@/data/mockData";
import { Book, FilePlus, Users, Award, BookUser, Lightbulb } from "lucide-react";
import { useEffect } from "react";

const Dashboard = () => {
  const publications = getPublicationsByResearcherId(currentUser.id);

  // Use effect to simulate loading data
  useEffect(() => {
    console.log("Dashboard loading data for researcher:", currentUser.orcidId);
  }, []);

  return (
    <Layout>
      <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back, {currentUser.name.split(" ")[0]}
            </p>
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
            <Button
              className="bg-orcid-green hover:bg-orcid-green/90"
              onClick={() => window.location.href = "/profile"}
            >
              View Profile
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricsCard
            title="Total Publications"
            value={currentUser.metrics.publications}
            icon={<Book className="h-4 w-4 text-gray-500" />}
            trend={{ value: 12, isPositive: true }}
          />
          <MetricsCard
            title="Citations"
            value={currentUser.metrics.citations}
            icon={<BookUser className="h-4 w-4 text-gray-500" />}
            trend={{ value: 23, isPositive: true }}
          />
          <MetricsCard
            title="h-index"
            value={currentUser.metrics.hIndex}
            icon={<Award className="h-4 w-4 text-gray-500" />}
            trend={{ value: 2, isPositive: true }}
          />
          <MetricsCard
            title="Network"
            value={currentUser.followers + currentUser.following}
            icon={<Users className="h-4 w-4 text-gray-500" />}
            description={`${currentUser.followers} followers, ${currentUser.following} following`}
          />
        </div>

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
      </div>
    </Layout>
  );
};

export default Dashboard;
