
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

interface RecentPublicationsProps {
  publications: Publication[];
  maxItems?: number;
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

const RecentPublications = ({ publications, maxItems = 5 }: RecentPublicationsProps) => {
  const displayPublications = publications.slice(0, maxItems);

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
          {displayPublications.length > 0 ? (
            displayPublications.map((publication) => (
              <div
                key={publication.id}
                className="border-b border-gray-100 pb-4 last:border-0 last:pb-0"
              >
                <div className="flex gap-3">
                  <div className="text-2xl">{publicationTypeIcons[publication.type]}</div>
                  <div className="flex-1">
                    <h3 className="text-md font-medium">{publication.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {publication.authors.join(", ")} ({publication.year})
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {publication.journal}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        Citations: {publication.citations}
                      </span>
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
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500">
                No publications added yet.
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
