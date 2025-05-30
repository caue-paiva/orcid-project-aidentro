"""
CrossRef API utility functions for DOI-based publication retrieval.

This module provides helper functions for interacting with the CrossRef API
to retrieve comprehensive publication metadata using DOIs.
"""

import requests
import json
from typing import Dict, List, Optional, Union
import urllib3


class PublicationAPIClient:
    """Client for retrieving publication metadata by DOI using CrossRef API."""
    
    def __init__(self, user_agent: str = None):
        """
        Initialize Publication API client.
        
        Args:
            user_agent: User agent string for API requests (recommended for better service)
        """
        self.base_url = "https://api.crossref.org"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': user_agent or 'ORCID-Project/1.0 (mailto:your-email@example.com)'
        }
    
    def _make_request(self, url, params=None):
        """
        Make HTTP request with SSL verification handling.
        
        Args:
            url: Request URL
            params: Query parameters
            
        Returns:
            Response JSON data
        """
        try:
            response = requests.get(url, headers=self.headers, params=params, verify=True)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.SSLError:
            # If SSL verification fails, try without verification (for testing environments)
            print("⚠️  SSL verification failed, retrying without verification...")
            # Disable SSL warnings for this request
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            response.raise_for_status()
            return response.json()
    
    def get_publication_by_doi(self, doi: str) -> Dict:
        """
        Get publication metadata by DOI from CrossRef.
        
        Args:
            doi: DOI of the publication (with or without doi: prefix)
            
        Returns:
            Publication metadata dictionary
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If DOI is invalid or not found
        """
        # Clean DOI - remove doi: prefix if present
        clean_doi = doi.replace('doi:', '') if doi.startswith('doi:') else doi
        
        url = f"{self.base_url}/works/{clean_doi}"
        
        try:
            data = self._make_request(url)
            return data.get('message', {})
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"DOI not found: {clean_doi}")
            else:
                raise requests.RequestException(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"API request failed: {e}")
    
    def get_publication_formatted(self, doi: str) -> Dict:
        """
        Get publication metadata formatted for easy use.
        
        Args:
            doi: DOI of the publication
            
        Returns:
            Formatted publication dictionary with common fields
        """
        raw_data = self.get_publication_by_doi(doi)
        
        # Extract and format common fields
        formatted = {
            'doi': raw_data.get('DOI'),
            'title': raw_data.get('title', ['Unknown Title'])[0] if raw_data.get('title') else 'Unknown Title',
            'authors': self._format_authors(raw_data.get('author', [])),
            'journal': raw_data.get('container-title', ['Unknown Journal'])[0] if raw_data.get('container-title') else 'Unknown Journal',
            'published_date': self._format_date(raw_data.get('published')),
            'published_online_date': self._format_date(raw_data.get('published-online')),
            'published_print_date': self._format_date(raw_data.get('published-print')),
            'type': raw_data.get('type'),
            'publisher': raw_data.get('publisher'),
            'issn': raw_data.get('ISSN', []),
            'isbn': raw_data.get('ISBN', []),
            'url': raw_data.get('URL'),
            'abstract': raw_data.get('abstract'),
            'volume': raw_data.get('volume'),
            'issue': raw_data.get('issue'),
            'page': raw_data.get('page'),
            'article_number': raw_data.get('article-number'),
            'citation_count': raw_data.get('is-referenced-by-count', 0),
            'reference_count': raw_data.get('references-count', 0),
            'license': self._format_license(raw_data.get('license', [])),
            'funding': self._format_funding(raw_data.get('funder', [])),
            'subjects': raw_data.get('subject', []),
            'language': raw_data.get('language'),
            'created_date': raw_data.get('created', {}).get('date-time'),
            'updated_date': raw_data.get('deposited', {}).get('date-time')
        }
        
        return formatted
    
    def _format_authors(self, authors: List[Dict]) -> List[Dict]:
        """Format author information."""
        formatted_authors = []
        for author in authors:
            formatted_author = {
                'given_name': author.get('given', ''),
                'family_name': author.get('family', ''),
                'full_name': f"{author.get('given', '')} {author.get('family', '')}".strip(),
                'orcid': author.get('ORCID'),
                'affiliation': [aff.get('name') for aff in author.get('affiliation', [])]
            }
            formatted_authors.append(formatted_author)
        return formatted_authors
    
    def _format_date(self, date_info: Dict) -> Optional[Dict]:
        """Format date information."""
        if not date_info or 'date-parts' not in date_info:
            return None
        
        date_parts = date_info['date-parts'][0] if date_info['date-parts'] else []
        if not date_parts:
            return None
        
        formatted_date = {
            'year': date_parts[0] if len(date_parts) > 0 else None,
            'month': date_parts[1] if len(date_parts) > 1 else None,
            'day': date_parts[2] if len(date_parts) > 2 else None,
            'raw': date_info
        }
        
        # Create a readable date string
        if formatted_date['year']:
            date_str = str(formatted_date['year'])
            if formatted_date['month']:
                date_str += f"-{formatted_date['month']:02d}"
                if formatted_date['day']:
                    date_str += f"-{formatted_date['day']:02d}"
            formatted_date['formatted'] = date_str
        
        return formatted_date
    
    def _format_license(self, licenses: List[Dict]) -> List[Dict]:
        """Format license information."""
        formatted_licenses = []
        for license_info in licenses:
            formatted_license = {
                'url': license_info.get('URL'),
                'start_date': self._format_date(license_info.get('start')),
                'delay_in_days': license_info.get('delay-in-days'),
                'content_version': license_info.get('content-version')
            }
            formatted_licenses.append(formatted_license)
        return formatted_licenses
    
    def _format_funding(self, funders: List[Dict]) -> List[Dict]:
        """Format funding information."""
        formatted_funding = []
        for funder in funders:
            formatted_funder = {
                'name': funder.get('name'),
                'doi': funder.get('DOI'),
                'awards': funder.get('award', [])
            }
            formatted_funding.append(formatted_funder)
        return formatted_funding
    
    def search_publications(self, query: str, rows: int = 20, offset: int = 0, 
                          sort: str = None, order: str = 'desc') -> Dict:
        """
        Search for publications using CrossRef API.
        
        Args:
            query: Search query string
            rows: Number of results to return (max 1000)
            offset: Starting offset for pagination (max 10000)
            sort: Sort field (relevance, updated, deposited, indexed, published, etc.)
            order: Sort order ('asc' or 'desc')
            
        Returns:
            Search results dictionary
        """
        url = f"{self.base_url}/works"
        params = {
            'query': query,
            'rows': min(rows, 1000),
            'offset': min(offset, 10000)
        }
        
        if sort:
            params['sort'] = sort
            params['order'] = order
        
        try:
            data = self._make_request(url, params)
            return data.get('message', {})
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Search request failed: {e}")
    
    def search_publications_by_author(self, author_name: str, rows: int = 20) -> Dict:
        """
        Search for publications by author name.
        
        Args:
            author_name: Author name to search for
            rows: Number of results to return
            
        Returns:
            Search results dictionary
        """
        query = f'query.author:"{author_name}"'
        return self.search_publications(query, rows=rows)
    
    def search_publications_by_title(self, title: str, rows: int = 20) -> Dict:
        """
        Search for publications by title.
        
        Args:
            title: Title to search for
            rows: Number of results to return
            
        Returns:
            Search results dictionary
        """
        query = f'query.bibliographic:"{title}"'
        return self.search_publications(query, rows=rows)
    
    def search_publications_by_journal(self, journal_name: str, rows: int = 20) -> Dict:
        """
        Search for publications by journal name.
        
        Args:
            journal_name: Journal name to search for
            rows: Number of results to return
            
        Returns:
            Search results dictionary
        """
        query = f'query.container-title:"{journal_name}"'
        return self.search_publications(query, rows=rows)
    
    def get_publication_references(self, doi: str) -> List[Dict]:
        """
        Get references cited by a publication (if available).
        
        Args:
            doi: DOI of the publication
            
        Returns:
            List of references
        """
        publication = self.get_publication_by_doi(doi)
        return publication.get('reference', [])
    
    def get_publication_citations(self, doi: str) -> Dict:
        """
        Get citation information for a publication.
        
        Args:
            doi: DOI of the publication
            
        Returns:
            Citation information dictionary
        """
        publication = self.get_publication_by_doi(doi)
        
        return {
            'doi': publication.get('DOI'),
            'title': publication.get('title', ['Unknown Title'])[0] if publication.get('title') else 'Unknown Title',
            'citation_count': publication.get('is-referenced-by-count', 0),
            'reference_count': publication.get('references-count', 0),
            'citation_url': f"https://api.crossref.org/works/{publication.get('DOI')}/citation"
        }
    
    def get_publication_summary(self, doi: str) -> Dict:
        """
        Get a concise summary of a publication for display purposes.
        
        Args:
            doi: DOI of the publication
            
        Returns:
            Publication summary dictionary
        """
        pub = self.get_publication_formatted(doi)
        
        # Create author list string
        author_names = [author['full_name'] for author in pub['authors']]
        authors_str = ', '.join(author_names[:3])  # Show first 3 authors
        if len(author_names) > 3:
            authors_str += f' et al. ({len(author_names)} total)'
        
        # Create publication year string
        pub_year = pub['published_date']['year'] if pub['published_date'] else 'Unknown'
        
        summary = {
            'doi': pub['doi'],
            'title': pub['title'],
            'authors': authors_str,
            'journal': pub['journal'],
            'year': pub_year,
            'type': pub['type'],
            'citation_count': pub['citation_count'],
            'url': pub['url'],
            'full_citation': f"{authors_str} ({pub_year}). {pub['title']}. {pub['journal']}."
        }
        
        return summary
    
    def bulk_get_publications(self, dois: List[str]) -> Dict[str, Dict]:
        """
        Get multiple publications by their DOIs.
        
        Args:
            dois: List of DOIs to retrieve
            
        Returns:
            Dictionary mapping DOIs to publication data
        """
        results = {}
        failed = []
        
        for doi in dois:
            try:
                pub_data = self.get_publication_formatted(doi)
                results[doi] = pub_data
            except Exception as e:
                failed.append({'doi': doi, 'error': str(e)})
        
        return {
            'successful': results,
            'failed': failed,
            'total_requested': len(dois),
            'successful_count': len(results),
            'failed_count': len(failed)
        }
    
    def get_journal_info(self, issn: str) -> Dict:
        """
        Get journal information by ISSN.
        
        Args:
            issn: ISSN of the journal (format: XXXX-XXXX)
            
        Returns:
            Journal information dictionary
        """
        url = f"{self.base_url}/journals/{issn}"
        
        try:
            data = self._make_request(url)
            return data.get('message', {})
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Journal lookup failed: {e}")
    
    def get_publisher_info(self, member_id: str) -> Dict:
        """
        Get publisher/member information.
        
        Args:
            member_id: CrossRef member ID
            
        Returns:
            Publisher information dictionary
        """
        url = f"{self.base_url}/members/{member_id}"
        
        try:
            data = self._make_request(url)
            return data.get('message', {})
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Publisher lookup failed: {e}")
    
    def check_doi_exists(self, doi: str) -> bool:
        """
        Check if a DOI exists in CrossRef registry.
        
        Args:
            doi: DOI to check
            
        Returns:
            True if DOI exists, False otherwise
        """
        try:
            self.get_publication_by_doi(doi)
            return True
        except (ValueError, requests.RequestException):
            return False
    
    @staticmethod
    def validate_doi_format(doi: str) -> bool:
        """
        Validate DOI format.
        
        Args:
            doi: DOI to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        import re
        
        if not doi:
            return False
        
        # Remove doi: prefix if present
        clean_doi = doi.replace('doi:', '') if doi.startswith('doi:') else doi
        
        # Basic DOI format: 10.XXXX/XXXXX
        pattern = r'^10\.\d{4,}/\S+$'
        return bool(re.match(pattern, clean_doi))
    
    @staticmethod
    def format_citation_apa(publication: Dict) -> str:
        """
        Format publication in APA citation style.
        
        Args:
            publication: Publication dictionary from get_publication_formatted()
            
        Returns:
            APA formatted citation string
        """
        authors = publication.get('authors', [])
        title = publication.get('title', 'Unknown Title')
        journal = publication.get('journal', 'Unknown Journal')
        year = publication.get('published_date', {}).get('year', 'n.d.') if publication.get('published_date') else 'n.d.'
        volume = publication.get('volume', '')
        issue = publication.get('issue', '')
        page = publication.get('page', '')
        doi = publication.get('doi', '')
        
        # Format authors
        if authors:
            if len(authors) == 1:
                author_str = f"{authors[0]['family_name']}, {authors[0]['given_name'][0]}." if authors[0]['given_name'] else authors[0]['family_name']
            elif len(authors) <= 7:
                author_list = []
                for author in authors[:-1]:
                    author_list.append(f"{author['family_name']}, {author['given_name'][0]}." if author['given_name'] else author['family_name'])
                last_author = authors[-1]
                last_author_str = f"{last_author['family_name']}, {last_author['given_name'][0]}." if last_author['given_name'] else last_author['family_name']
                author_str = ', '.join(author_list) + f', & {last_author_str}'
            else:
                # More than 7 authors
                first_six = authors[:6]
                last_author = authors[-1]
                author_list = []
                for author in first_six:
                    author_list.append(f"{author['family_name']}, {author['given_name'][0]}." if author['given_name'] else author['family_name'])
                last_author_str = f"{last_author['family_name']}, {last_author['given_name'][0]}." if last_author['given_name'] else last_author['family_name']
                author_str = ', '.join(author_list) + f', ... {last_author_str}'
        else:
            author_str = 'Unknown Author'
        
        # Build citation
        citation = f"{author_str} ({year}). {title}. *{journal}*"
        
        # Add volume and issue
        if volume:
            citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"
        
        # Add pages
        if page:
            citation += f", {page}"
        
        # Add DOI
        if doi:
            citation += f". https://doi.org/{doi}"
        
        return citation
