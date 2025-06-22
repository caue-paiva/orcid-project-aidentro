import { useState, useEffect } from "react";
import Layout from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { countries, institutions } from "@/data/mockData";
import { Researcher } from "@/types";
import { Book, Filter, Search as SearchIcon, SlidersHorizontal, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group";

// Import new utilities for ORCID integration
import { buildORCIDQuery, applyClientSideFilters } from "@/utils/orcidQueryBuilder";
import { searchResearchers, SearchResearchersResponse } from "@/api/orcidApi";

const Search = () => {
  const [query, setQuery] = useState("");
  const [nameQuery, setNameQuery] = useState("");
  const [institution, setInstitution] = useState("");
  const [country, setCountry] = useState("");
  const [expertise, setExpertise] = useState<string[]>([]);
  const [minPublications, setMinPublications] = useState(0);
  const [minCitations, setMinCitations] = useState(0);
  const [sortBy, setSortBy] = useState("relevance");
  const [showFilters, setShowFilters] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Lista de áreas de especialidade para o filtro
  const expertiseAreas = [
    "Natural Language Processing",
    "Machine Learning",
    "Computer Vision",
    "Artificial Intelligence",
    "Data Science",
    "Computational Linguistics",
    "Bioinformatics",
    "Computer Graphics",
    "Human-Computer Interaction",
    "Robotics",
    "Information Retrieval",
    "Network Security",
  ];

  // Sample auto-complete suggestions based on query
  useEffect(() => {
    if (query && query.length >= 2) {
      const expertise = [
        "Natural Language Processing",
        "Machine Learning",
        "Computer Vision",
        "Artificial Intelligence",
        "Data Science",
        "Computational Linguistics",
      ];
      
      const names = [
        "Maria Silva",
        "Mario Santos",
        "Maria Pereira",
        "Marco Aurelio",
        "Michelle Smith",
      ];
      
      const suggestedTerms = [...expertise, ...names].filter((term) =>
        term.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5);
      
      setSuggestions(suggestedTerms);
    } else {
      setSuggestions([]);
    }
  }, [query]);

  const handleSearch = async (startIndex: number = 0) => {
    setIsSearching(true);
    setSuggestions([]);
    setSearchError(null);
    
    try {
      // Combine main query with name query if both are provided
      let combinedQuery = "";
      
      if (query.trim() && nameQuery.trim()) {
        // Both fields have content - combine them with AND
        combinedQuery = `(${query.trim()}) AND (given-names:${nameQuery.trim()} OR family-name:${nameQuery.trim()} OR credit-name:"${nameQuery.trim()}")`;
      } else if (nameQuery.trim()) {
        // Only name query provided
        combinedQuery = `given-names:${nameQuery.trim()} OR family-name:${nameQuery.trim()} OR credit-name:"${nameQuery.trim()}"`;
      } else if (query.trim()) {
        // Only main query provided
        combinedQuery = query.trim();
      } else {
        // No query provided - search all (will be filtered by other criteria)
        combinedQuery = "*";
      }

      // Build ORCID query from frontend filters
      const orcidQuery = buildORCIDQuery({
        query: combinedQuery,
        institution: institution !== "any" ? institution : undefined,
        country: country !== "any" ? country : undefined,
        expertise: expertise.length > 0 ? expertise : undefined,
        minPublications,
        minCitations,
        sortBy
      });

      console.log('🔍 Built ORCID query:', orcidQuery.q);

      // Call ORCID API through backend
      const response: SearchResearchersResponse = await searchResearchers({
        q: orcidQuery.q,
        rows: 20,
        start: startIndex
      });

      if (!response.success) {
        throw new Error(response.error || 'Search failed');
      }

      console.log('📊 Raw search results:', response.search_results);

      // Apply client-side filters for features not supported by ORCID API
      const filteredResults = applyClientSideFilters(
        response.search_results.results,
        {
          minPublications,
          minCitations,
          sortBy
        }
      );

      console.log('✅ Filtered results:', filteredResults);

      // Convert to frontend format
      const formattedResults = filteredResults.map(researcher => ({
        id: researcher.orcid_id,
        orcidId: researcher.orcid_id,
        name: researcher.display_name,
        institutionName: researcher.current_affiliation || "Independent Researcher",
        countryCode: "", // Not available from ORCID search
        country: "", // Not available from ORCID search
        department: "",
        position: "",
        email: "",
        avatarUrl: "",
        biography: "",
        website: researcher.profile_url,
        socialLinks: {},
        areaOfExpertise: [], // Would need additional API calls
        metrics: {
          publications: researcher.works_count || 0,
          citations: 0, // Not available from basic search
          hIndex: 0, // Not available from basic search
        },
        followers: 0,
        following: 0,
        isCompleteProfile: true,
        onboardingStep: 4,
        // Additional fields from ORCID
        given_names: researcher.given_names,
        family_name: researcher.family_name,
        credit_name: researcher.credit_name,
        profile_url: researcher.profile_url,
        orcid_uri: researcher.orcid_uri,
        error: researcher.error
      }));

      setResults(formattedResults);
      setTotalResults(response.search_results.total_results);
      setCurrentPage(Math.floor(startIndex / 20));

      if (formattedResults.length === 0 && query) {
        toast.info("No researchers found matching your criteria. Try adjusting your search terms.");
      } else if (formattedResults.length > 0) {
        toast.success(`Found ${response.search_results.total_results} researchers`);
      }

    } catch (error: any) {
      console.error('❌ Search error:', error);
      setSearchError(error.message || 'Search failed. Please try again.');
      setResults([]);
      setTotalResults(0);
      toast.error('Search failed. Please check your connection and try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };



  const handleFollow = (researcher: any) => {
    toast.success(`Now following ${researcher.name}`);
  };

  const toggleExpertise = (area: string) => {
    setExpertise(prev => 
      prev.includes(area) 
        ? prev.filter(item => item !== area)
        : [...prev, area]
    );
  };

  const clearFilters = () => {
    setInstitution("");
    setCountry("");
    setExpertise([]);
    setMinPublications(0);
    setMinCitations(0);
    setSortBy("relevance");
  };

  const loadNextPage = () => {
    const nextStart = (currentPage + 1) * 20;
    handleSearch(nextStart);
  };

  const loadPreviousPage = () => {
    const prevStart = Math.max(0, (currentPage - 1) * 20);
    handleSearch(prevStart);
  };

  return (
    <Layout>
      <div className="px-4 py-8 md:px-6 lg:px-8 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Find Researchers</h1>

        <div className="bg-white rounded-2xl shadow-md p-6 mb-8">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="md:col-span-2 relative">
              <Input
                placeholder="Search researchers, institutions, or topics (e.g., 'Machine Learning', 'family-name:Smith')"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full"
              />
              {suggestions.length > 0 && (
                <div className="absolute z-10 mt-1 w-full bg-white border rounded-md shadow-lg">
                  <ul>
                    {suggestions.map((suggestion, index) => (
                      <li
                        key={index}
                        className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                        onClick={() => {
                          setQuery(suggestion);
                          setSuggestions([]);
                        }}
                      >
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <Select value={institution} onValueChange={setInstitution}>
              <SelectTrigger>
                <SelectValue placeholder="Institution (any)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="any">Any institution</SelectItem>
                {institutions.map((inst) => (
                  <SelectItem key={inst.value} value={inst.value}>
                    {inst.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={country} onValueChange={setCountry}>
              <SelectTrigger>
                <SelectValue placeholder="Country (any)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="any">Any country</SelectItem>
                {countries.map((c) => (
                  <SelectItem key={c.value} value={c.value}>
                    {c.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Search by Name Section */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Search by Name</h3>
            <Input
              placeholder="Enter researcher name (e.g., 'John Smith', 'Maria Garcia')"
              value={nameQuery}
              onChange={(e) => setNameQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              This field will be included when you click the main Search button below
            </p>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
            <Collapsible
              open={showFilters}
              onOpenChange={setShowFilters}
              className="w-full"
            >
              <div className="flex items-center gap-2">
                <CollapsibleTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-1">
                    <Filter className="h-4 w-4" />
                    {showFilters ? "Hide Filters" : "Show Advanced Filters"}
                  </Button>
                </CollapsibleTrigger>
                
                {(expertise.length > 0 || minPublications > 0 || minCitations > 0) && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={clearFilters}
                    className="text-gray-500"
                  >
                    Clear filters
                  </Button>
                )}
              </div>

              <CollapsibleContent className="mt-4 space-y-4">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {/* Expertise Areas Filter */}
                  <div className="space-y-2">
                    <Label className="font-medium">Research Areas</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button 
                          variant="outline" 
                          className="w-full justify-between"
                        >
                          Select research areas
                          <SlidersHorizontal className="h-4 w-4 ml-2" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-80 p-0" align="start">
                        <div className="p-4 max-h-[300px] overflow-auto">
                          <div className="grid grid-cols-1 gap-2">
                            {expertiseAreas.map((area) => (
                              <div key={area} className="flex items-center space-x-2">
                                <Checkbox 
                                  id={`expertise-${area}`} 
                                  checked={expertise.includes(area)}
                                  onCheckedChange={() => toggleExpertise(area)}
                                />
                                <Label htmlFor={`expertise-${area}`} className="text-sm">
                                  {area}
                                </Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </PopoverContent>
                    </Popover>
                    {expertise.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {expertise.map(area => (
                          <div key={area} className="bg-gray-100 text-xs py-1 px-2 rounded-full">
                            {area}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Minimum Publications */}
                  <div className="space-y-2">
                    <Label htmlFor="min-publications" className="font-medium">Minimum Publications</Label>
                    <Select 
                      value={minPublications.toString()} 
                      onValueChange={(val) => setMinPublications(Number(val))}
                    >
                      <SelectTrigger id="min-publications">
                        <SelectValue placeholder="Any number" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0">Any number</SelectItem>
                        <SelectItem value="5">At least 5</SelectItem>
                        <SelectItem value="10">At least 10</SelectItem>
                        <SelectItem value="25">At least 25</SelectItem>
                        <SelectItem value="50">At least 50</SelectItem>
                        <SelectItem value="100">At least 100</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Minimum Citations */}
                  <div className="space-y-2">
                    <Label htmlFor="min-citations" className="font-medium">Minimum Citations</Label>
                    <Select 
                      value={minCitations.toString()} 
                      onValueChange={(val) => setMinCitations(Number(val))}
                    >
                      <SelectTrigger id="min-citations">
                        <SelectValue placeholder="Any number" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0">Any number</SelectItem>
                        <SelectItem value="10">At least 10</SelectItem>
                        <SelectItem value="50">At least 50</SelectItem>
                        <SelectItem value="100">At least 100</SelectItem>
                        <SelectItem value="500">At least 500</SelectItem>
                        <SelectItem value="1000">At least 1,000</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Sort Options */}
                <div className="border-t pt-4">
                  <Label className="block mb-2 font-medium">Sort Results By</Label>
                  <RadioGroup 
                    value={sortBy} 
                    onValueChange={setSortBy}
                    className="flex flex-wrap gap-4"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="relevance" id="sort-relevance" />
                      <Label htmlFor="sort-relevance">Relevance</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="publications" id="sort-publications" />
                      <Label htmlFor="sort-publications">Publications</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="citations" id="sort-citations" />
                      <Label htmlFor="sort-citations">Citations</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="hIndex" id="sort-hindex" />
                      <Label htmlFor="sort-hindex">h-index</Label>
                    </div>
                  </RadioGroup>
                </div>
              </CollapsibleContent>
            </Collapsible>

            <Button
              onClick={() => handleSearch()}
              className="bg-orcid-green hover:bg-orcid-green/90 ml-auto"
              disabled={isSearching}
            >
              <SearchIcon className="mr-2 h-4 w-4" />
              {isSearching ? "Searching..." : "Search"}
            </Button>
          </div>

          {/* Search Error Display */}
          {searchError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm">
                <strong>Search Error:</strong> {searchError}
              </p>
              <p className="text-red-600 text-xs mt-1">
                Try simplifying your search terms or check your internet connection.
              </p>
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">
                Search Results ({totalResults.toLocaleString()})
              </h2>
              
              {/* Pagination Controls */}
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadPreviousPage}
                  disabled={currentPage === 0 || isSearching}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-600">
                  Page {currentPage + 1}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadNextPage}
                  disabled={((currentPage + 1) * 20) >= totalResults || isSearching}
                >
                  Next
                </Button>
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {results.map((researcher) => (
                <Card key={researcher.id} className="overflow-hidden hover:shadow-md transition-shadow">
                  <CardHeader className="pb-4">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center space-x-4">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={researcher.avatarUrl} alt={researcher.name} />
                          <AvatarFallback>{researcher.name.substring(0, 2)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <Link to={`/profile/${researcher.id}`}>
                            <CardTitle className="text-lg hover:text-orcid-green">
                              {researcher.name}
                            </CardTitle>
                          </Link>
                          <CardDescription>
                            {researcher.institutionName || "Independent Researcher"}
                          </CardDescription>
                          {researcher.error && (
                            <p className="text-xs text-red-500 mt-1">
                              {researcher.error}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pb-4">
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <span className="flex items-center">
                        <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                          />
                        </svg>
                        <a 
                          href={researcher.profile_url || researcher.orcid_uri} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-orcid-green hover:underline"
                        >
                          ORCID Profile
                        </a>
                      </span>
                    </div>
                    
                    <div className="mt-3 flex space-x-4 text-sm">
                      <span className="flex items-center">
                        <Book className="h-4 w-4 mr-1 text-gray-500" />
                        <strong>{researcher.metrics.publications}</strong> publications
                      </span>
                    </div>
                  </CardContent>
                  <CardFooter className="bg-gray-50 border-t pt-3 pb-3 flex justify-between">
                    <div className="flex gap-2">
                      <a 
                        href={researcher.profile_url || researcher.orcid_uri}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button variant="ghost" size="sm">View ORCID</Button>
                      </a>
                      <Link
                        to={`/dashboard-social?orcid_id=${encodeURIComponent(researcher.orcidId)}&name=${encodeURIComponent(researcher.name)}&institution=${encodeURIComponent(researcher.institutionName || '')}`}
                      >
                        <Button variant="ghost" size="sm" className="text-blue-600 hover:bg-blue-50">
                          View Dashboard
                        </Button>
                      </Link>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleFollow(researcher)}
                      className="text-orcid-green hover:bg-orcid-green/10"
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Follow
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        )}

        {query && !isSearching && results.length === 0 && !searchError && (
          <div className="text-center py-10">
            <div className="text-gray-400 mb-4">
              <SearchIcon className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No results found</h3>
            <p className="text-gray-600">
              We couldn't find any researchers matching your search criteria.
              <br />
              Try adjusting your search terms or filters.
            </p>
          </div>
        )}

        {!query && !results.length && (
          <div className="text-center py-12">
            <div className="text-gray-300 mb-4">
              <SearchIcon className="h-16 w-16 mx-auto" />
            </div>
            <h2 className="text-xl font-semibold mb-2">
              Search for researchers
            </h2>
            <p className="text-gray-600 max-w-md mx-auto">
              Find researchers by name, institution, research area, or country.
              <br />
              You can also use advanced ORCID syntax like "family-name:Smith" or "affiliation-org-name:University".
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Search;
