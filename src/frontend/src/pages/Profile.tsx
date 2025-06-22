
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import ResearcherProfile from "@/components/profile/ResearcherProfile";
import { getResearcherById, getPublicationsByResearcherId, currentUser } from "@/data/mockData";
import { Researcher } from "@/types";

const Profile = () => {
  // Get the researcher ID from the URL parameters
  const { id } = useParams<{ id: string }>();
  const [researcher, setResearcher] = useState<Researcher | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResearcher = async () => {
      setLoading(true);
      try {
        // If no ID is provided, show the current user's profile
        const loadedResearcher = id ? getResearcherById(id) : currentUser;
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setResearcher(loadedResearcher || null);
      } catch (error) {
        console.error("Error loading researcher:", error);
      } finally {
        setLoading(false);
      }
    };

    loadResearcher();
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="animate-pulse flex flex-col items-center">
            <div className="h-12 w-12 rounded-full bg-gray-200 mb-4"></div>
            <div className="h-8 w-48 bg-gray-200 rounded mb-3"></div>
            <div className="h-4 w-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!researcher) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Researcher Not Found</h1>
          <p className="mt-2 text-gray-600">
            We couldn't find the researcher you're looking for. They may have changed their ORCID iD or profile.
          </p>
        </div>
      </Layout>
    );
  }

  const publications = getPublicationsByResearcherId(researcher.id);

  return (
    <Layout>
      <ResearcherProfile researcher={researcher} publications={publications} />
    </Layout>
  );
};

export default Profile;
