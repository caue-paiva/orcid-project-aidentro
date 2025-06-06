export interface Researcher {
  id: string;
  orcidId: string;
  name: string;
  institutionName: string;
  countryCode: string;
  country: string;
  department?: string;
  position?: string;
  email?: string;
  avatarUrl?: string;
  biography?: string;
  website?: string;
  socialLinks?: {
    twitter?: string;
    linkedin?: string;
    googleScholar?: string;
    researchGate?: string;
    github?: string;
  };
  areaOfExpertise: string[];
  metrics: {
    publications: number;
    citations: number;
    hIndex: number;
  };
  followers: number;
  following: number;
  isCompleteProfile: boolean;
  onboardingStep: number;
}

export interface Publication {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  doi?: string;
  citations: number;
  abstract?: string;
  keywords?: string[];
  link?: string;
  type: 'journal-article' | 'conference-paper' | 'book' | 'book-chapter' | 'preprint' | 'dataset' | 'code';
}

export interface ResearcherSearchParams {
  query?: string;
  institution?: string;
  country?: string;
  expertise?: string;
  page?: number;
  limit?: number;
}

export interface CitationData {
  year: number;
  citations: number;
  cumulativeCitations: number;
}

export interface CitationMetrics {
  total_citations: number;
  citation_trend?: {
    value: number;
    isPositive: boolean;
  };
  avg_citations_per_year: number;
  h_index_approximation: number;
  publications_count: number;
  cited_publications_count: number;
  citation_chart_data: CitationData[];
  analysis_success: boolean;
  error?: string;
}

export interface CitationAnalysis {
  yearlyData: CitationData[];
  totalCitations: number;
  totalPublications: number;
  publicationsWithCitations: number;
  successfulLookups: number;
  analysisPeriod: string;
  error?: string;
}
