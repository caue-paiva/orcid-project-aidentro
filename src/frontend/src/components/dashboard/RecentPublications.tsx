
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Publication } from "@/types";
import { ResearcherPaper } from "@/api/orcidApi";

interface RecentPublicationsProps {
  publications?: Publication[];
  papers?: ResearcherPaper[];
  maxItems?: number;
  isLoading?: boolean;
}

const publicationTypeIcons: Record<Publication["type"], string> = {
  "journal-article": "📄",
  "conference-paper": "🎤",
  "book": "📚",
  "book-chapter": "📖",
  "preprint": "📝",
  "dataset": "📊",
  "code": "💻",
};

const RecentPublications = ({ publications = [], papers = [], maxItems = 5, isLoading = false }: RecentPublicationsProps) => {
  // Convert ResearcherPaper to Publication format
  const convertedPapers: Publication[] = papers.map((paper, index) => ({
    id: `paper-${index}`,
    title: paper.title,
    authors: [], // Authors not available in the API response
    journal: paper.journal || '',
    year: paper.publication_year,
    doi: paper.dois.length > 0 ? paper.dois[0] : undefined,
    citations: 0, // Citations not available in basic API response
    type: paper.type as Publication['type'],
    link: paper.url,
  }));

  // Combine both publication sources
  const allPublications = [...publications, ...convertedPapers];
  const displayPublications = allPublications.slice(0, maxItems);

  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Recent Publications</CardTitle>
        <CardDescription>
          Your latest research outputs
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {isLoading ? (
            <div className="text-center py-4">
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orcid-green"></div>
                <p className="text-gray-500">Loading publications...</p>
              </div>
            </div>
          ) : displayPublications.length > 0 ? (
            displayPublications.map((publication) => (
              <div
                key={publication.id}
                className="border-b border-gray-100 pb-4 last:border-0 last:pb-0"
              >
                <div className="flex gap-3">
                  <div className="text-2xl">{publicationTypeIcons[publication.type] || "📄"}</div>
                  <div className="flex-1">
                    <h3 className="text-md font-medium">{publication.title}</h3>
                    {publication.authors.length > 0 && (
                      <p className="text-sm text-gray-600 mt-1">
                        {publication.authors.join(", ")} ({publication.year})
                      </p>
                    )}
                    {!publication.authors.length && (
                      <p className="text-sm text-gray-600 mt-1">
                        Published in {publication.year}
                      </p>
                    )}
                    {publication.journal && (
                      <p className="text-sm text-gray-600 mt-1">
                        {publication.journal}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-2">
                      {publication.citations > 0 && (
                        <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          Citations: {publication.citations}
                        </span>
                      )}
                      {publication.doi && (
                        <a
                          href={`https://doi.org/${publication.doi}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-orcid-green hover:underline"
                        >
                          DOI: {publication.doi}
                        </a>
                      )}
                      {publication.link && (
                        <a
                          href={publication.link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          View Publication
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500">
                No publications found.
              </p>
            </div>
          )}
        </div>
        
        <div className="mt-6 flex justify-center">
          <Link to="/publications">
            <Button variant="outline">View all publications</Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentPublications;
