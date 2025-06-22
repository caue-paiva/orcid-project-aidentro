interface SearchFilters {
  query?: string;
  institution?: string;
  country?: string;
  expertise?: string[];
  minPublications?: number;
  minCitations?: number;
  sortBy?: string;
}

interface ORCIDQueryParams {
  q: string;
  rows?: number;
  start?: number;
}

/**
 * Escapes special characters in Lucene query strings
 * Special characters: + - && || ! ( ) { } [ ] ^ " ~ * ? : \ /
 */
function escapeLuceneSpecialChars(text: string): string {
  if (!text) return '';
  
  // List of special characters that need escaping in Lucene
  const specialChars = /[+\-&|!(){}\[\]^"~*?:\\\/]/g;
  
  return text.replace(specialChars, '\\$&');
}

/**
 * Wraps a value in quotes if it contains spaces or special characters
 */
function quoteIfNeeded(value: string): string {
  if (!value) return '';
  
  // Quote if contains spaces, special chars, or is already a phrase
  if (value.includes(' ') || value.includes('-') || value.includes('.')) {
    return `"${escapeLuceneSpecialChars(value)}"`;
  }
  
  return escapeLuceneSpecialChars(value);
}

/**
 * Converts frontend search filters to ORCID Lucene query syntax
 */
export function buildORCIDQuery(filters: SearchFilters): ORCIDQueryParams {
  const queryParts: string[] = [];
  
  // 1. Main text query - search across multiple fields
  if (filters.query && filters.query.trim()) {
    const mainQuery = filters.query.trim();
    
    // Check if it's already a structured query (contains field names with colons)
    if (mainQuery.includes(':')) {
      // User provided structured query, use as-is but escape values
      queryParts.push(mainQuery);
    } else {
      // Convert to multi-field search
      const escapedQuery = quoteIfNeeded(mainQuery);
      
      // Search across common fields
      const textSearchFields = [
        `given-names:${escapedQuery}`,
        `family-name:${escapedQuery}`,
        `credit-name:${escapedQuery}`,
        `other-names:${escapedQuery}`,
        `text:${escapedQuery}` // General text search
      ];
      
      // Use OR to search across multiple name fields
      queryParts.push(`(${textSearchFields.join(' OR ')})`);
    }
  }
  
  // 2. Institution filter
  if (filters.institution && filters.institution !== 'any') {
    const institutionQuery = quoteIfNeeded(filters.institution);
    queryParts.push(`affiliation-org-name:${institutionQuery}`);
  }
  
  // 3. Country filter - map country codes/names to ORCID format
  if (filters.country && filters.country !== 'any') {
    // Note: ORCID uses country codes, but frontend might use names
    // You might need to map country names to ISO codes
    const countryQuery = quoteIfNeeded(filters.country);
    queryParts.push(`affiliation-org-country:${countryQuery}`);
  }
  
  // 4. Research areas/expertise - search in keywords and other relevant fields
  if (filters.expertise && filters.expertise.length > 0) {
    const expertiseQueries = filters.expertise.map(area => {
      const escapedArea = quoteIfNeeded(area);
      // Search in keywords, work titles, and general text
      return `(keyword:${escapedArea} OR work-titles:${escapedArea} OR text:${escapedArea})`;
    });
    
    // Use OR for multiple expertise areas (researcher can have any of these)
    queryParts.push(`(${expertiseQueries.join(' OR ')})`);
  }
  
  // Note: minPublications and minCitations cannot be directly filtered in ORCID search
  // These would need to be applied client-side after getting the enriched results
  
  // Combine all query parts with AND
  let finalQuery = queryParts.length > 0 ? queryParts.join(' AND ') : '*:*';
  
  // If no specific query was provided, use a broad search
  if (!finalQuery || finalQuery.trim() === '') {
    finalQuery = '*:*';
  }
  
  return {
    q: finalQuery
  };
}

/**
 * Converts frontend sort option to ORCID-compatible sorting
 * Note: ORCID API has limited sorting options, mostly relevance-based
 */
export function getORCIDSortParams(sortBy: string): Record<string, any> {
  // ORCID API doesn't support custom sorting like publications/citations count
  // These would need to be handled client-side after enrichment
  
  switch (sortBy) {
    case 'relevance':
    default:
      return {}; // Default relevance sorting
  }
}

/**
 * Applies client-side filters that cannot be handled by ORCID API
 */
export function applyClientSideFilters(
  results: any[], 
  filters: SearchFilters
): any[] {
  let filteredResults = [...results];
  
  // Filter by minimum publications
  if (filters.minPublications && filters.minPublications > 0) {
    filteredResults = filteredResults.filter(researcher => 
      (researcher.works_count || 0) >= filters.minPublications
    );
  }
  
  // Filter by minimum citations  
  if (filters.minCitations && filters.minCitations > 0) {
    filteredResults = filteredResults.filter(researcher => 
      (researcher.total_citations || 0) >= filters.minCitations
    );
  }
  
  // Apply sorting (since ORCID API doesn't support custom sorting)
  if (filters.sortBy) {
    switch (filters.sortBy) {
      case 'publications':
        filteredResults.sort((a, b) => (b.works_count || 0) - (a.works_count || 0));
        break;
      case 'citations':
        filteredResults.sort((a, b) => (b.total_citations || 0) - (a.total_citations || 0));
        break;
      case 'hIndex':
        filteredResults.sort((a, b) => (b.h_index || 0) - (a.h_index || 0));
        break;
      case 'relevance':
      default:
        // Keep original order (relevance from ORCID)
        break;
    }
  }
  
  return filteredResults;
}

/**
 * Example usage and common query patterns
 */
export const ORCIDQueryExamples = {
  // Basic name search
  nameSearch: (firstName: string, lastName: string) => 
    `given-names:"${escapeLuceneSpecialChars(firstName)}" AND family-name:"${escapeLuceneSpecialChars(lastName)}"`,
  
  // Institution search
  institutionSearch: (institution: string) => 
    `affiliation-org-name:"${escapeLuceneSpecialChars(institution)}"`,
  
  // Keyword/expertise search
  keywordSearch: (keyword: string) => 
    `keyword:"${escapeLuceneSpecialChars(keyword)}"`,
  
  // DOI search
  doiSearch: (doi: string) => 
    `digital-object-ids:"${escapeLuceneSpecialChars(doi)}"`,
  
  // Combined search
  combinedSearch: (name: string, institution: string) => 
    `(given-names:"${escapeLuceneSpecialChars(name)}" OR family-name:"${escapeLuceneSpecialChars(name)}") AND affiliation-org-name:"${escapeLuceneSpecialChars(institution)}"`,
  
  // Wildcard search
  wildcardSearch: (partialName: string) => 
    `family-name:${escapeLuceneSpecialChars(partialName)}*`,
  
  // Range search (for dates)
  dateRangeSearch: (startYear: number, endYear: number) => 
    `profile-submission-date:[${startYear}-01-01T00:00:00Z TO ${endYear}-12-31T23:59:59Z]`
};

export default {
  buildORCIDQuery,
  getORCIDSortParams,
  applyClientSideFilters,
  ORCIDQueryExamples,
  escapeLuceneSpecialChars,
  quoteIfNeeded
}; 