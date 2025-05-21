
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Researcher, Publication } from "@/types";
import { Bell, MessageSquare, Share2, UserPlus, Mail, Check } from "lucide-react";

interface ResearcherProfileProps {
  researcher: Researcher;
  publications: Publication[];
}

const ResearcherProfile = ({ researcher, publications }: ResearcherProfileProps) => {
  const [isFollowing, setIsFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState("publications");

  const handleFollow = () => {
    setIsFollowing(!isFollowing);
    toast.success(
      isFollowing
        ? `Unfollowed ${researcher.name}`
        : `Now following ${researcher.name}. You'll receive updates about new publications.`
    );
  };

  const handleContact = () => {
    toast.info(`Contact form for ${researcher.name} would open here`);
  };

  const handleShare = () => {
    // Mock share functionality
    navigator.clipboard.writeText(
      `https://orcid.org/${researcher.orcidId}`
    );
    toast.success("Profile link copied to clipboard!");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Profile header */}
      <div className="bg-white shadow rounded-2xl overflow-hidden">
        <div className="h-32 bg-gradient-to-r from-orcid-green/80 to-orcid-green"></div>
        <div className="p-6">
          <div className="sm:flex sm:items-center sm:justify-between">
            <div className="sm:flex sm:space-x-5">
              <div className="-mt-12 sm:-mt-16 relative">
                <Avatar className="h-24 w-24 border-4 border-white">
                  <AvatarImage src={researcher.avatarUrl} alt={researcher.name} />
                  <AvatarFallback className="text-xl">
                    {researcher.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-sm">
                  <div className="h-6 w-6 rounded-full bg-orcid-green flex items-center justify-center">
                    <span className="font-bold text-white text-xs">ID</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 sm:mt-0 text-center sm:text-left">
                <div className="flex items-center">
                  <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                    {researcher.name}
                  </h1>
                  {researcher.isCompleteProfile && (
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <Check className="w-3 h-3 mr-1" />
                      Verified
                    </span>
                  )}
                </div>
                <p className="text-gray-500 mt-1">
                  {researcher.position && `${researcher.position}${researcher.department ? ", " : ""}`}
                  {researcher.department && researcher.department}
                  {(researcher.position || researcher.department) && " at "}
                  {researcher.institutionName}
                </p>
                <p className="text-gray-500 text-sm mt-1">
                  {researcher.country}
                  <span className="mx-2">•</span>
                  <span className="text-orcid-green">
                    {researcher.orcidId}
                  </span>
                </p>
              </div>
            </div>
            <div className="mt-5 sm:mt-0 flex flex-wrap gap-2 sm:gap-3 justify-center sm:justify-end">
              <Button
                variant={isFollowing ? "outline" : "default"}
                className={
                  isFollowing
                    ? "border-orcid-green text-orcid-green hover:bg-orcid-green/10"
                    : "bg-orcid-green hover:bg-orcid-green/90"
                }
                onClick={handleFollow}
              >
                {isFollowing ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Following
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Follow
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={handleContact}>
                <Mail className="h-4 w-4 mr-2" />
                Contact
              </Button>
              <Button variant="ghost" onClick={handleShare}>
                <Share2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Metrics and tags */}
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-gray-200 pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {researcher.metrics.publications}
              </p>
              <p className="text-sm text-gray-500">Publications</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {researcher.metrics.citations}
              </p>
              <p className="text-sm text-gray-500">Citations</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {researcher.metrics.hIndex}
              </p>
              <p className="text-sm text-gray-500">h-index</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {researcher.followers}
              </p>
              <p className="text-sm text-gray-500">Followers</p>
            </div>
          </div>

          {/* Research areas */}
          <div className="mt-6">
            <div className="flex flex-wrap gap-2 mt-2">
              {researcher.areaOfExpertise.map((area) => (
                <Badge key={area} variant="outline" className="bg-gray-50 text-gray-700">
                  {area}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="mt-8">
        <Tabs defaultValue="publications" onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 mb-8">
            <TabsTrigger value="publications">Publications</TabsTrigger>
            <TabsTrigger value="about">About</TabsTrigger>
            <TabsTrigger value="network">Network</TabsTrigger>
            <TabsTrigger value="datasets">Datasets</TabsTrigger>
          </TabsList>
          
          {/* Publications Tab */}
          <TabsContent value="publications" className="mt-6">
            <div className="bg-white shadow rounded-xl p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Publications</h2>
                <div className="flex gap-3">
                  {/* Sort and filter options could go here */}
                </div>
              </div>

              {publications.length > 0 ? (
                <div className="space-y-8">
                  {publications.map((pub) => (
                    <div key={pub.id} className="border-b border-gray-100 pb-6 last:border-0">
                      <h3 className="text-lg font-medium hover:text-orcid-green">
                        <a href={pub.link} target="_blank" rel="noopener noreferrer">
                          {pub.title}
                        </a>
                      </h3>
                      <p className="text-gray-600 mt-1">
                        {pub.authors.join(", ")}
                      </p>
                      <p className="text-gray-500 text-sm mt-1">
                        {pub.journal}, {pub.year}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                          Citations: {pub.citations}
                        </Badge>
                        {pub.doi && (
                          <Badge variant="outline" className="bg-gray-50">
                            DOI: {pub.doi}
                          </Badge>
                        )}
                        <Badge variant="outline" className="bg-gray-50">
                          {pub.type.replace("-", " ")}
                        </Badge>
                      </div>
                      {pub.abstract && (
                        <div className="mt-3">
                          <p className="text-gray-700 text-sm line-clamp-3">
                            {pub.abstract}
                          </p>
                          <button className="text-xs text-orcid-green mt-1 hover:underline">
                            Read more
                          </button>
                        </div>
                      )}
                    </div>
                  ))}

                  <div className="mt-4 flex justify-center">
                    <Button variant="outline">Load more publications</Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-10">
                  <p className="text-gray-500">No publications available</p>
                </div>
              )}
            </div>
          </TabsContent>
          
          {/* About Tab */}
          <TabsContent value="about">
            <div className="bg-white shadow rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">About</h2>
              
              {researcher.biography ? (
                <div className="mb-6">
                  <h3 className="text-md font-medium mb-2">Biography</h3>
                  <p className="text-gray-700">{researcher.biography}</p>
                </div>
              ) : (
                <p className="text-gray-500 italic mb-6">No biography provided</p>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-md font-medium mb-2">Education</h3>
                  <p className="text-gray-500 italic">Education information not provided</p>
                </div>
                
                <div>
                  <h3 className="text-md font-medium mb-2">Contact</h3>
                  {researcher.email ? (
                    <p className="text-gray-700">{researcher.email}</p>
                  ) : (
                    <p className="text-gray-500 italic">Contact information not provided</p>
                  )}
                  
                  {researcher.website && (
                    <div className="mt-2">
                      <a href={researcher.website} target="_blank" rel="noopener noreferrer" className="text-orcid-green hover:underline">
                        {researcher.website}
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Network Tab */}
          <TabsContent value="network">
            <div className="bg-white shadow rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-6">Network</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-md font-medium mb-3 flex items-center">
                    <UserPlus className="h-4 w-4 mr-2 text-gray-500" />
                    Followers ({researcher.followers})
                  </h3>
                  <p className="text-gray-500">
                    Researchers who follow {researcher.name.split(" ")[0]}'s work
                  </p>
                  <Button variant="link" className="mt-2 pl-0 text-orcid-green">
                    View all followers
                  </Button>
                </div>
                
                <div>
                  <h3 className="text-md font-medium mb-3 flex items-center">
                    <Bell className="h-4 w-4 mr-2 text-gray-500" />
                    Following ({researcher.following})
                  </h3>
                  <p className="text-gray-500">
                    Researchers that {researcher.name.split(" ")[0]} follows
                  </p>
                  <Button variant="link" className="mt-2 pl-0 text-orcid-green">
                    View all following
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Datasets Tab */}
          <TabsContent value="datasets">
            <div className="bg-white shadow rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-6">Datasets & Code</h2>
              
              <div className="text-center py-8">
                <p className="text-gray-500">
                  No datasets or code repositories available yet
                </p>
                
                {researcher.id === "1" && (
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => toast.info("Upload dataset functionality would open here")}
                  >
                    Upload a dataset
                  </Button>
                )}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ResearcherProfile;
