"""
Google Scholar API utility functions for citation metrics.

This module provides functions to extract citation data from Google Scholar
using web scraping via the scholarly library.
"""

import time
from typing import Dict, List, Optional, Union
from datetime import datetime
import requests
from dataclasses import dataclass

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("⚠️  Warning: 'scholarly' library not installed. Install with: pip install scholarly")
    scholarly = None


@dataclass
class CitationData:
    """Data class for citation information"""
    year: int
    citations: int
    cumulative_citations: int = 0


@dataclass
class AuthorMetrics:
    """Data class for author metrics"""
    name: str
    scholar_id: Optional[str]
    total_citations: int
    h_index: int
    i10_index: int
    citations_per_year: Dict[int, int]
    publications_count: int


class GoogleScholarAPI:
    """Client for interacting with Google Scholar via scholarly library"""
    
    def __init__(self, use_proxy: bool = False, delay: float = 1.0):
        """
        Initialize Google Scholar API client.
        
        Args:
            use_proxy: Whether to use proxy for requests (helps avoid rate limiting)
            delay: Delay between requests in seconds
        """
        if not scholarly:
            raise ImportError("scholarly library is required. Install with: pip install scholarly")
        
        self.delay = delay
        self.use_proxy = use_proxy
        
        if use_proxy:
            try:
                # Set up proxy to avoid rate limiting
                pg = ProxyGenerator()
                pg.FreeProxies()
                scholarly.use_proxy(pg)
                print("✅ Proxy configured for Google Scholar requests")
            except Exception as e:
                print(f"⚠️  Warning: Could not set up proxy: {e}")
    
    def search_author(self, author_name: str, affiliation: str = None) -> Optional[Dict]:
        """
        Search for an author on Google Scholar.
        
        Args:
            author_name: Name of the author to search for
            affiliation: Optional affiliation to help narrow search
            
        Returns:
            Author information dictionary or None if not found
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.delay)
            
            # Search for author
            search_query = scholarly.search_author(author_name)
            
            # Get first result
            author = next(search_query, None)
            
            if author:
                # Get detailed author information
                author_detail = scholarly.fill(author)
                return self._format_author_data(author_detail)
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching for author '{author_name}': {e}")
            return None
    
    def get_author_by_id(self, scholar_id: str) -> Optional[Dict]:
        """
        Get author information by Google Scholar ID.
        
        Args:
            scholar_id: Google Scholar author ID
            
        Returns:
            Author information dictionary or None if not found
        """
        try:
            time.sleep(self.delay)
            
            # Get author by ID
            author = scholarly.search_author_id(scholar_id)
            author_detail = scholarly.fill(author)
            
            return self._format_author_data(author_detail)
            
        except Exception as e:
            print(f"❌ Error getting author by ID '{scholar_id}': {e}")
            return None
    
    def get_citations_by_year(self, author_name: str, target_year: int, 
                             affiliation: str = None) -> Optional[int]:
        """
        Get citation count for a specific year.
        
        Args:
            author_name: Name of the author
            target_year: Year to get citations for
            affiliation: Optional affiliation to help identify correct author
            
        Returns:
            Citation count for the specified year or None if not found
        """
        author_data = self.search_author(author_name, affiliation)
        
        if not author_data:
            return None
        
        citations_per_year = author_data.get('citations_per_year', {})
        return citations_per_year.get(target_year, 0)
    
    def get_citations_for_years(self, author_name: str, years: List[int], 
                               affiliation: str = None) -> Dict[int, int]:
        """
        Get citation counts for multiple years.
        
        Args:
            author_name: Name of the author
            years: List of years to get citations for
            affiliation: Optional affiliation
            
        Returns:
            Dictionary mapping year to citation count
        """
        author_data = self.search_author(author_name, affiliation)
        
        if not author_data:
            return {}
        
        citations_per_year = author_data.get('citations_per_year', {})
        
        result = {}
        for year in years:
            result[year] = citations_per_year.get(year, 0)
        
        return result
    
    def get_cumulative_citations(self, author_name: str, years: List[int], 
                                affiliation: str = None) -> List[CitationData]:
        """
        Get cumulative citation data over multiple years.
        
        Args:
            author_name: Name of the author
            years: List of years (should be sorted)
            affiliation: Optional affiliation
            
        Returns:
            List of CitationData objects with cumulative counts
        """
        citations_by_year = self.get_citations_for_years(author_name, sorted(years), affiliation)
        
        cumulative_data = []
        cumulative_total = 0
        
        for year in sorted(years):
            year_citations = citations_by_year.get(year, 0)
            cumulative_total += year_citations
            
            cumulative_data.append(CitationData(
                year=year,
                citations=year_citations,
                cumulative_citations=cumulative_total
            ))
        
        return cumulative_data
    
    def get_author_metrics(self, author_name: str, affiliation: str = None) -> Optional[AuthorMetrics]:
        """
        Get comprehensive author metrics.
        
        Args:
            author_name: Name of the author
            affiliation: Optional affiliation
            
        Returns:
            AuthorMetrics object with all available metrics
        """
        author_data = self.search_author(author_name, affiliation)
        
        if not author_data:
            return None
        
        return AuthorMetrics(
            name=author_data.get('name', author_name),
            scholar_id=author_data.get('scholar_id'),
            total_citations=author_data.get('total_citations', 0),
            h_index=author_data.get('h_index', 0),
            i10_index=author_data.get('i10_index', 0),
            citations_per_year=author_data.get('citations_per_year', {}),
            publications_count=len(author_data.get('publications', []))
        )
    
    def search_publications(self, author_name: str, limit: int = 20) -> List[Dict]:
        """
        Search for publications by an author.
        
        Args:
            author_name: Name of the author
            limit: Maximum number of publications to return
            
        Returns:
            List of publication dictionaries
        """
        try:
            author_data = self.search_author(author_name)
            
            if not author_data:
                return []
            
            publications = author_data.get('publications', [])
            
            # Get detailed information for first few publications
            detailed_pubs = []
            for i, pub in enumerate(publications[:limit]):
                if i > 0:
                    time.sleep(self.delay)
                
                try:
                    # Fill publication details
                    pub_detail = scholarly.fill(pub)
                    detailed_pubs.append(self._format_publication_data(pub_detail))
                except Exception as e:
                    print(f"⚠️  Could not get details for publication {i+1}: {e}")
                    # Add basic info even if detailed fetch fails
                    detailed_pubs.append(self._format_publication_data(pub))
            
            return detailed_pubs
            
        except Exception as e:
            print(f"❌ Error searching publications for '{author_name}': {e}")
            return []
    
    def _format_author_data(self, author_data: Dict) -> Dict:
        """Format author data from scholarly into standardized format"""
        return {
            'name': author_data.get('name', ''),
            'scholar_id': author_data.get('scholar_id', ''),
            'affiliation': author_data.get('affiliation', ''),
            'email': author_data.get('email', ''),
            'total_citations': author_data.get('citedby', 0),
            'h_index': author_data.get('hindex', 0),
            'i10_index': author_data.get('i10index', 0),
            'citations_per_year': author_data.get('cites_per_year', {}),
            'publications': author_data.get('publications', []),
            'interests': author_data.get('interests', [])
        }
    
    def _format_publication_data(self, pub_data: Dict) -> Dict:
        """Format publication data from scholarly into standardized format"""
        return {
            'title': pub_data.get('bib', {}).get('title', ''),
            'authors': pub_data.get('bib', {}).get('author', ''),
            'venue': pub_data.get('bib', {}).get('venue', ''),
            'year': pub_data.get('bib', {}).get('pub_year'),
            'citations': pub_data.get('num_citations', 0),
            'url': pub_data.get('pub_url', ''),
            'abstract': pub_data.get('bib', {}).get('abstract', '')
        }


# Convenience functions for easy usage
def get_author_citations_by_year(author_name: str, year: int, affiliation: str = None) -> Optional[int]:
    """
    Convenience function to get citations for a specific year.
    
    Args:
        author_name: Name of the author
        year: Year to get citations for
        affiliation: Optional affiliation
        
    Returns:
        Citation count for the specified year
    """
    api = GoogleScholarAPI()
    return api.get_citations_by_year(author_name, year, affiliation)


def get_author_citations_for_years(author_name: str, years: List[int], 
                                  affiliation: str = None) -> Dict[int, int]:
    """
    Convenience function to get citations for multiple years.
    
    Args:
        author_name: Name of the author
        years: List of years to get citations for
        affiliation: Optional affiliation
        
    Returns:
        Dictionary mapping year to citation count
    """
    api = GoogleScholarAPI()
    return api.get_citations_for_years(author_name, years, affiliation)


def get_cumulative_citations(author_name: str, years: List[int], 
                           affiliation: str = None) -> List[CitationData]:
    """
    Convenience function to get cumulative citation data.
    
    Args:
        author_name: Name of the author
        years: List of years (will be sorted automatically)
        affiliation: Optional affiliation
        
    Returns:
        List of CitationData objects with cumulative counts
    """
    api = GoogleScholarAPI()
    return api.get_cumulative_citations(author_name, years, affiliation)


def get_complete_author_metrics(author_name: str, affiliation: str = None) -> Optional[AuthorMetrics]:
    """
    Convenience function to get complete author metrics.
    
    Args:
        author_name: Name of the author
        affiliation: Optional affiliation
        
    Returns:
        AuthorMetrics object with all available data
    """
    api = GoogleScholarAPI()
    return api.get_author_metrics(author_name, affiliation) 