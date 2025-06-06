"""
ORCID API utility functions.

This module provides helper functions for interacting with the ORCID Public API
using access tokens obtained through the OAuth flow, and CrossRef API for
publication metadata retrieval by DOI.
"""

import requests
import json
from typing import Dict, List, Optional, Union
from decouple import config
import urllib3
from datetime import datetime
from collections import defaultdict
import time


class ORCIDAPIClient:
    """Client for interacting with ORCID Public API, instantiated with a given access token or orcid_id """
    
    def __init__(self, access_token: str, orcid_id: str, base_url: str = None):
        """
        Initialize ORCID API client.
        
        Args:
            access_token: Valid ORCID access token (can be empty for public API calls)
            orcid_id: ORCID identifier (mandatory)
            base_url: ORCID base URL (defaults to config value)
        """
        if not orcid_id:
            raise ValueError("ORCID ID is required")
        
        self.access_token = access_token
        self.orcid_id = orcid_id
        # Use production by default since many ORCID IDs are from production
        self.base_url = base_url or config('ORCID_BASE_URL', default='https://orcid.org')
        
        # Convert to public API URL
        if 'sandbox.orcid.org' in self.base_url:
            self.api_base_url = 'https://pub.sandbox.orcid.org/v3.0'
        else:
            self.api_base_url = 'https://pub.orcid.org/v3.0'
        
        # Set headers - only include Authorization if we have a token
        self.headers = {'Accept': 'application/json'}
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
    
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
    
    def search_researchers(self, query: str, rows: int = 20, start: int = 0) -> Dict:
        """
        Search for researchers in the ORCID registry.
        
        Args:
            query: Search query using Solr/Lucene syntax
            rows: Number of results to return (max 1000)
            start: Starting offset for pagination
            
        Returns:
            Search results dictionary
            
        Example:
            client.search_researchers('family-name:Smith AND affiliation-org-name:"University"')
        """
        url = f"{self.api_base_url}/search/"
        params = {
            'q': query,
            'rows': min(rows, 1000),  # ORCID max is 1000
            'start': start
        }
        
        return self._make_request(url, params)
    
    def get_researcher_record(self) -> Dict:
        """
        Get a researcher's complete public record.
        
        Returns:
            Complete ORCID record dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}"
        
        return self._make_request(url)
    
    def get_researcher_person_info(self) -> Dict:
        """
        Get a researcher's personal information (names, keywords, etc.).
        
        Returns:
            Person information dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/person"
        
        return self._make_request(url)
    
    def get_researcher_works(self) -> Dict:
        """
        Get a researcher's works (publications, datasets, etc.).
        
        Returns:
            Works summary dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/works"
        
        return self._make_request(url)
    
    def get_researcher_employments(self) -> Dict:
        """
        Get a researcher's employment history.
        
        Returns:
            Employment history dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/employments"
        
        return self._make_request(url)
    
    def get_researcher_education(self) -> Dict:
        """
        Get a researcher's education history.
        
        Returns:
            Education history dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/educations"
        
        return self._make_request(url)
    
    def get_researcher_funding(self) -> Dict:
        """
        Get a researcher's funding information.
        
        Returns:
            Funding information dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/fundings"
        
        return self._make_request(url)
    
    def get_researcher_activities(self) -> Dict:
        """
        Get a summary of all researcher's activities (works, funding, education, employment, etc.).
        
        Returns:
            Activities summary dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/activities"
        
        return self._make_request(url)
    
    def get_researcher_peer_reviews(self) -> Dict:
        """
        Get a researcher's peer review activities.
        
        Returns:
            Peer reviews dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/peer-reviews"
        
        return self._make_request(url)
    
    def get_researcher_research_resources(self) -> Dict:
        """
        Get a researcher's research resources.
        
        Returns:
            Research resources dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/research-resources"
        
        return self._make_request(url)
    
    def get_researcher_distinctions(self) -> Dict:
        """
        Get a researcher's distinctions and honors.
        
        Returns:
            Distinctions dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/distinctions"
        
        return self._make_request(url)
    
    def get_researcher_invited_positions(self) -> Dict:
        """
        Get a researcher's invited positions.
        
        Returns:
            Invited positions dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/invited-positions"
        
        return self._make_request(url)
    
    def get_researcher_memberships(self) -> Dict:
        """
        Get a researcher's memberships.
        
        Returns:
            Memberships dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/memberships"
        
        return self._make_request(url)
    
    def get_researcher_services(self) -> Dict:
        """
        Get a researcher's services.
        
        Returns:
            Services dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/services"
        
        return self._make_request(url)
    
    def get_researcher_qualifications(self) -> Dict:
        """
        Get a researcher's qualifications.
        
        Returns:
            Qualifications dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/qualifications"
        
        return self._make_request(url)
    
    def _clean_orcid_id(self, orcid_id: str) -> str:
        """
        Clean ORCID iD to standard format.
        
        Args:
            orcid_id: ORCID identifier (with or without URI prefix)
            
        Returns:
            Clean ORCID iD in format 0000-0000-0000-0000
        """
        if not orcid_id:
            raise ValueError("ORCID iD cannot be empty")
        
        # Remove URI prefix if present
        if orcid_id.startswith('https://orcid.org/'):
            orcid_id = orcid_id.replace('https://orcid.org/', '')
        elif orcid_id.startswith('http://orcid.org/'):
            orcid_id = orcid_id.replace('http://orcid.org/', '')
        
        return orcid_id
    
    def search_researchers_by_name(self, given_name: str = None, 
                                  family_name: str = None, **kwargs) -> List[Dict]:
        """
        Search for researchers by name.
        
        Args:
            given_name: Given name to search for
            family_name: Family name to search for
            **kwargs: Additional search parameters
            
        Returns:
            List of researcher records
        """
        # Build search query
        query_parts = []
        if given_name:
            query_parts.append(f'given-names:"{given_name}"')
        if family_name:
            query_parts.append(f'family-name:"{family_name}"')
        
        if not query_parts:
            raise ValueError("At least one name parameter must be provided")
        
        query = ' AND '.join(query_parts)
        
        # Add additional search parameters
        for key, value in kwargs.items():
            if value:
                query += f' AND {key}:"{value}"'
        
        results = self.search_researchers(query)
        return results.get('result', [])
    
    def search_researchers_by_affiliation(self, organization: str, **kwargs) -> List[Dict]:
        """
        Search for researchers by affiliation.
        
        Args:
            organization: Organization name to search for
            **kwargs: Additional search parameters
            
        Returns:
            List of researcher records
        """
        query = f'affiliation-org-name:"{organization}"'
        
        # Add additional search parameters
        for key, value in kwargs.items():
            if value:
                query += f' AND {key}:"{value}"'
        
        results = self.search_researchers(query)
        return results.get('result', [])
    
    def get_researcher_summary(self, include_all_sections: bool = False) -> Dict:
        """
        Get a comprehensive summary of a researcher's profile.
        
        Args:
            include_all_sections: If True, includes all available sections (slower but more complete)
            
        Returns:
            Researcher summary dictionary with person info, works, employments, etc.
        """
        
        try:
            # Get basic person information
            person_info = self.get_researcher_person_info()
            
            # Get core sections
            sections = {}
            
            # Works (publications, datasets, etc.)
            try:
                works = self.get_researcher_works()
                sections['works'] = works
                sections['works_count'] = len(works.get('group', []))
            except:
                sections['works'] = {'group': []}
                sections['works_count'] = 0
            
            # Employment history
            try:
                employments = self.get_researcher_employments()
                sections['employments'] = employments
                sections['employments_count'] = len(employments.get('affiliation-group', []))
            except:
                sections['employments'] = {'affiliation-group': []}
                sections['employments_count'] = 0
            
            # Education history
            try:
                education = self.get_researcher_education()
                sections['education'] = education
                sections['education_count'] = len(education.get('affiliation-group', []))
            except:
                sections['education'] = {'affiliation-group': []}
                sections['education_count'] = 0
            
            # Funding
            try:
                funding = self.get_researcher_funding()
                sections['funding'] = funding
                sections['funding_count'] = len(funding.get('group', []))
            except:
                sections['funding'] = {'group': []}
                sections['funding_count'] = 0
            
            if include_all_sections:
                # Additional sections for comprehensive profile
                additional_sections = [
                    ('activities', self.get_researcher_activities),
                    ('peer_reviews', self.get_researcher_peer_reviews),
                    ('research_resources', self.get_researcher_research_resources),
                    ('distinctions', self.get_researcher_distinctions),
                    ('invited_positions', self.get_researcher_invited_positions),
                    ('memberships', self.get_researcher_memberships),
                    ('services', self.get_researcher_services),
                    ('qualifications', self.get_researcher_qualifications)
                ]
                
                for section_name, method in additional_sections:
                    try:
                        section_data = method()
                        sections[section_name] = section_data
                        # Count items based on common ORCID structure
                        if 'affiliation-group' in section_data:
                            sections[f'{section_name}_count'] = len(section_data.get('affiliation-group', []))
                        elif 'group' in section_data:
                            sections[f'{section_name}_count'] = len(section_data.get('group', []))
                        else:
                            sections[f'{section_name}_count'] = 0
                    except:
                        sections[section_name] = {}
                        sections[f'{section_name}_count'] = 0
            
            # Build comprehensive summary
            summary = {
                'orcid_id': self.orcid_id,
                'person': person_info,
                **sections
            }
            
            return summary
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch researcher summary: {e}")
    
    def get_researcher_works_for_cv(self) -> List[Dict]:
        """
        Get researcher's works formatted for CV generation.
        
        Returns:
            List of formatted works for CV
        """
        works_data = self.get_researcher_works()
        
        formatted_works = []
        for group in works_data.get('group', []):
            for work_summary in group.get('work-summary', []):
                work_info = {
                    'title': work_summary.get('title', {}).get('title', {}).get('value', 'Unknown Title'),
                    'type': work_summary.get('type', 'Unknown Type'),
                    'publication_date': work_summary.get('publication-date'),
                    'journal': work_summary.get('journal-title', {}).get('value') if work_summary.get('journal-title') else None,
                    'external_ids': work_summary.get('external-ids', {}).get('external-id', []),
                    'url': work_summary.get('url', {}).get('value') if work_summary.get('url') else None
                }
                formatted_works.append(work_info)
        
        return formatted_works
    
    def get_researcher_affiliations_for_cv(self) -> Dict:
        """
        Get researcher's affiliations (employment + education) formatted for CV.
        
        Returns:
            Dictionary with employment and education data formatted for CV
        """
        # Get employment
        employment_data = self.get_researcher_employments()
        formatted_employment = []
        for group in employment_data.get('affiliation-group', []):
            for summary in group.get('summaries', []):
                emp_info = {
                    'organization': summary.get('organization', {}).get('name', 'Unknown Organization'),
                    'role': summary.get('role-title', 'Unknown Role'),
                    'start_date': summary.get('start-date'),
                    'end_date': summary.get('end-date'),
                    'department': summary.get('department-name')
                }
                formatted_employment.append(emp_info)
        
        # Get education
        education_data = self.get_researcher_education()
        formatted_education = []
        for group in education_data.get('affiliation-group', []):
            for summary in group.get('summaries', []):
                edu_info = {
                    'organization': summary.get('organization', {}).get('name', 'Unknown Institution'),
                    'role': summary.get('role-title', 'Unknown Degree'),
                    'start_date': summary.get('start-date'),
                    'end_date': summary.get('end-date'),
                    'department': summary.get('department-name')
                }
                formatted_education.append(edu_info)
        
        return {
            'employment': formatted_employment,
            'education': formatted_education
        }
    
    def search_researchers_advanced(self, **search_params) -> List[Dict]:
        """
        Advanced search for researchers with multiple parameters.
        
        Args:
            **search_params: Search parameters (given_name, family_name, affiliation, keyword, etc.)
            
        Returns:
            List of researcher records
        """
        # Build advanced search query
        query_parts = []
        
        # Map common parameters to ORCID field names
        field_mapping = {
            'given_name': 'given-names',
            'family_name': 'family-name',
            'affiliation': 'affiliation-org-name',
            'keyword': 'keyword',
            'email': 'email',
            'orcid': 'orcid'
        }
        
        for param, value in search_params.items():
            if value and param in field_mapping:
                field_name = field_mapping[param]
                if param == 'orcid':
                    query_parts.append(f'{field_name}:{value}')
                else:
                    query_parts.append(f'{field_name}:"{value}"')
        
        if not query_parts:
            raise ValueError("At least one search parameter must be provided")
        
        query = ' AND '.join(query_parts)
        results = self.search_researchers(query)
        return results.get('result', [])
    
    @staticmethod
    def validate_orcid_id_format(orcid_id: str) -> bool:
        """
        Validate ORCID iD format.
        
        Args:
            orcid_id: ORCID identifier to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        import re
        
        if not orcid_id:
            return False
        
        # Remove any URI prefix if present
        if orcid_id.startswith('https://orcid.org/'):
            orcid_id = orcid_id.replace('https://orcid.org/', '')
        elif orcid_id.startswith('http://orcid.org/'):
            orcid_id = orcid_id.replace('http://orcid.org/', '')
        
        # Check format: 0000-0000-0000-000X
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        return bool(re.match(pattern, orcid_id))
    
    def search_researchers_by_doi(self, doi: str, **kwargs) -> List[Dict]:
        """
        Search for researchers who have a specific DOI in their works.
        
        Args:
            doi: DOI to search for (with or without doi: prefix)
            **kwargs: Additional search parameters
            
        Returns:
            List of researcher records that include this DOI
        """
        # Clean DOI - remove doi: prefix if present
        clean_doi = doi.replace('doi:', '') if doi.startswith('doi:') else doi
        
        query = f'digital-object-ids:"{clean_doi}"'
        
        # Add additional search parameters
        for key, value in kwargs.items():
            if value:
                query += f' AND {key}:"{value}"'
        
        results = self.search_researchers(query)
        return results.get('result', [])
    
    def find_researchers_with_publication(self, doi: str, rows: int = 20) -> Dict:
        """
        Find researchers who have claimed a specific publication (by DOI).
        
        Args:
            doi: DOI of the publication to search for
            rows: Number of results to return
            
        Returns:
            Dictionary with search results and researcher information
        """
        # Clean DOI
        clean_doi = doi.replace('doi:', '') if doi.startswith('doi:') else doi
        
        query = f'digital-object-ids:"{clean_doi}"'
        results = self.search_researchers(query, rows=rows)
        
        # Format results for easier consumption
        formatted_results = {
            'doi': clean_doi,
            'total_found': results.get('num-found', 0),
            'researchers': []
        }
        
        for item in results.get('result', []):
            researcher = {
                'orcid_id': item.get('orcid-identifier', {}).get('path'),
                'name': None,
                'institution': None
            }
            
            # Extract name if available
            if 'given-names' in item and 'family-names' in item:
                given = item['given-names']['value'] if item.get('given-names') else ''
                family = item['family-names']['value'] if item.get('family-names') else ''
                researcher['name'] = f"{given} {family}".strip()
            
            # Extract current institution if available
            if 'institution-name' in item:
                researcher['institution'] = item['institution-name'].get('value')
            
            formatted_results['researchers'].append(researcher)
        
        return formatted_results

    def get_personal_details(self) -> Dict:
        """
        Get a researcher's personal details (name, biography, etc.).
        
        Returns:
            Personal details dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/personal-details"
        
        return self._make_request(url)
    
    def get_emails(self) -> Dict:
        """
        Get a researcher's email addresses.
        
        Returns:
            Email addresses dictionary
        """
        clean_orcid_id = self._clean_orcid_id(self.orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/emails"
        
        return self._make_request(url)
    
    def get_user_identity_info(self) -> Dict:
        """
        Get essential user identity information from ORCID record.
        
        Returns:
            Dictionary containing:
            - name: Full name (given + family or credit name)
            - current_affiliation: Main current employment
            - email: Primary email address
            - location: Current work location
        """
        try:
            # 1. Get Name from personal-details
            personal_details = self.get_personal_details()
            name_info = personal_details.get('name', {})
            
            # Prefer credit-name if available, otherwise combine given + family names
            if name_info.get('credit-name') and name_info['credit-name'].get('value'):
                full_name = name_info['credit-name']['value']
            else:
                given_names = name_info.get('given-names', {}).get('value', '') if name_info.get('given-names') else ''
                family_name = name_info.get('family-name', {}).get('value', '') if name_info.get('family-name') else ''
                full_name = f"{given_names} {family_name}".strip()
            
            # 2. Get Primary Email
            try:
                emails_data = self.get_emails()
                primary_email = None
                
                for email in emails_data.get('email', []):
                    if email.get('primary', False):
                        primary_email = email.get('email')
                        break
                
                # If no primary email found, take the first available email
                if not primary_email and emails_data.get('email'):
                    primary_email = emails_data['email'][0].get('email')
                    
            except Exception:
                primary_email = None
            
            # 3. Get Current Affiliation (employment with no end-date)
            try:
                employments = self.get_researcher_employments()
                current_affiliation = None
                current_location = None
                
                for group in employments.get('affiliation-group', []):
                    for summary_wrapper in group.get('summaries', []):
                        # The actual employment data is inside 'employment-summary'
                        summary = summary_wrapper.get('employment-summary', {})
                        
                        # Check if this is a current employment (no end-date)
                        if not summary.get('end-date'):
                            organization = summary.get('organization', {})
                            current_affiliation = organization.get('name')
                            
                            # Get location info
                            address = organization.get('address', {})
                            location_parts = []
                            if address.get('city'):
                                location_parts.append(address['city'])
                            if address.get('region'):
                                location_parts.append(address['region'])
                            if address.get('country'):
                                location_parts.append(address['country'])
                            
                            current_location = ', '.join(location_parts) if location_parts else None
                            break
                    
                    if current_affiliation:
                        break
                        
            except Exception:
                current_affiliation = None
                current_location = None
            
            # Build user identity info
            user_identity = {
                'orcid_id': self.orcid_id,
                'name': full_name or 'Name not available',
                'email': primary_email,
                'current_affiliation': current_affiliation,
                'current_location': current_location,
                'profile_url': f"https://orcid.org/{self._clean_orcid_id(self.orcid_id)}"
            }
            
            return user_identity
            
        except Exception as e:
            # Return basic info even if detailed lookup fails
            return {
                'orcid_id': self.orcid_id,
                'name': 'Unable to retrieve name',
                'email': None,
                'current_affiliation': None,
                'current_location': None,
                'profile_url': f"https://orcid.org/{self._clean_orcid_id(self.orcid_id)}",
                'error': str(e)
            }

    def get_citation_analysis(self, years_back: int = 5, max_publications: int = 20, timeout_per_request: int = 10) -> Dict:
        """
        Get citation analysis data showing citations per year and cumulative totals.
        
        Args:
            years_back: Number of years back to analyze (default 5)
            max_publications: Maximum number of publications to process (default 20)
            timeout_per_request: Timeout in seconds for each API request (default 10)
            
        Returns:
            Dictionary containing:
            - yearly_data: List of {year, citations, cumulative_citations}
            - total_citations: Total citation count
            - total_publications: Total number of publications with DOIs
            - publications_with_citations: Number of publications that have been cited
        """
        from .crossref_api import PublicationAPIClient
        
        analysis_start_time = time.time()
        max_analysis_time = 45  # Maximum time for entire analysis (45 seconds)
        
        try:
            # Get researcher's works
            print("🔄 Fetching researcher works from ORCID...")
            works_data = self.get_researcher_works()
            crossref_client = PublicationAPIClient()
            
            # Extract DOIs from works
            publications_with_dois = []
            current_year = datetime.now().year
            start_year = current_year - years_back + 1
            
            for group in works_data.get('group', []):
                for work_summary in group.get('work-summary', []):
                    # Extract DOIs from external identifiers
                    external_ids = work_summary.get('external-ids', {}).get('external-id', [])
                    dois = []
                    
                    for ext_id in external_ids:
                        if ext_id.get('external-id-type') == 'doi':
                            dois.append(ext_id.get('external-id-value'))
                    
                    # Get publication year
                    pub_date = work_summary.get('publication-date')
                    pub_year = None
                    if pub_date and pub_date.get('year'):
                        pub_year = int(pub_date['year']['value'])
                    
                    # Store publication info with DOIs
                    if dois:
                        for doi in dois:
                            publications_with_dois.append({
                                'doi': doi,
                                'title': work_summary.get('title', {}).get('title', {}).get('value', 'Unknown Title'),
                                'publication_year': pub_year,
                                'journal': work_summary.get('journal-title', {}).get('value') if work_summary.get('journal-title') else None
                            })
            
            # Limit publications to prevent timeouts
            if len(publications_with_dois) > max_publications:
                print(f"⚠️  Limiting analysis to {max_publications} publications (found {len(publications_with_dois)})")
                # Sort by publication year (newest first) and take the most recent
                publications_with_dois.sort(key=lambda x: x['publication_year'] or 0, reverse=True)
                publications_with_dois = publications_with_dois[:max_publications]
            
            print(f"📊 Analyzing {len(publications_with_dois)} publications with DOIs")
            
            # Get citation data for each publication
            citations_by_year = defaultdict(int)
            total_citations = 0
            publications_with_citations = 0
            successful_lookups = 0
            failed_lookups = 0
            
            for i, pub in enumerate(publications_with_dois):
                # Check if we're running out of time
                elapsed_time = time.time() - analysis_start_time
                if elapsed_time > max_analysis_time:
                    print(f"⏰ Analysis timeout reached ({elapsed_time:.1f}s), stopping at {i+1}/{len(publications_with_dois)} publications")
                    break
                
                try:
                    # Get citation count from CrossRef with timeout
                    print(f"🔍 Looking up citations for DOI {i+1}/{len(publications_with_dois)}: {pub['doi'][:50]}...")
                    
                    start_request = time.time()
                    citation_info = crossref_client.get_publication_citations(pub['doi'])
                    request_time = time.time() - start_request
                    
                    citation_count = citation_info.get('citation_count', 0)
                    
                    if citation_count > 0:
                        publications_with_citations += 1
                        total_citations += citation_count
                        
                        # For simplicity, attribute all citations to the publication year
                        pub_year = pub['publication_year']
                        if pub_year and pub_year >= start_year:
                            citations_by_year[pub_year] += citation_count
                        
                        print(f"  ✅ Found {citation_count} citations ({request_time:.1f}s)")
                    else:
                        print(f"  📄 No citations found ({request_time:.1f}s)")
                    
                    successful_lookups += 1
                    
                    # Brief pause to avoid overwhelming APIs
                    time.sleep(0.1)
                    
                except Exception as e:
                    failed_lookups += 1
                    print(f"  ❌ Failed to get citations for DOI {pub['doi']}: {str(e)[:100]}")
                    # Don't break the entire analysis for one failed DOI
                    continue
            
            total_analysis_time = time.time() - analysis_start_time
            print(f"📈 Analysis completed in {total_analysis_time:.1f}s:")
            print(f"  • Successful lookups: {successful_lookups}/{len(publications_with_dois)}")
            print(f"  • Failed lookups: {failed_lookups}")
            print(f"  • Total citations found: {total_citations}")
            
            # Build yearly data with cumulative totals
            yearly_data = []
            cumulative_total = 0
            
            for year in range(start_year, current_year + 1):
                year_citations = citations_by_year.get(year, 0)
                cumulative_total += year_citations
                
                yearly_data.append({
                    'year': year,
                    'citations': year_citations,
                    'cumulative_citations': cumulative_total
                })
            
            # If no citation data found, generate minimal data structure
            if total_citations == 0:
                print("📊 No citation data found, generating minimal structure")
                yearly_data = []
                for year in range(start_year, current_year + 1):
                    yearly_data.append({
                        'year': year,
                        'citations': 0,
                        'cumulative_citations': 0
                    })
            
            return {
                'yearly_data': yearly_data,
                'total_citations': total_citations,
                'total_publications': len(publications_with_dois),
                'publications_with_citations': publications_with_citations,
                'successful_lookups': successful_lookups,
                'failed_lookups': failed_lookups,
                'analysis_period': f"{start_year}-{current_year}",
                'analysis_time_seconds': round(total_analysis_time, 1),
                'limited_analysis': len(publications_with_dois) >= max_publications
            }
            
        except Exception as e:
            error_time = time.time() - analysis_start_time
            print(f"❌ Error in citation analysis after {error_time:.1f}s: {e}")
            # Return empty structure on error
            current_year = datetime.now().year
            start_year = current_year - years_back + 1
            
            yearly_data = []
            for year in range(start_year, current_year + 1):
                yearly_data.append({
                    'year': year,
                    'citations': 0,
                    'cumulative_citations': 0
                })
            
            return {
                'yearly_data': yearly_data,
                'total_citations': 0,
                'total_publications': 0,
                'publications_with_citations': 0,
                'successful_lookups': 0,
                'failed_lookups': 0,
                'analysis_period': f"{start_year}-{current_year}",
                'analysis_time_seconds': round(error_time, 1),
                'error': str(e)
            }

    def get_citation_metrics_for_dashboard(self) -> Dict:
        """
        Get citation metrics formatted for dashboard display.
        
        Returns:
            Dictionary containing metrics for dashboard cards and charts
        """
        try:
            citation_analysis = self.get_citation_analysis()
            yearly_data = citation_analysis['yearly_data']
            
            # Calculate metrics
            total_citations = citation_analysis['total_citations']
            current_year = datetime.now().year
            
            # Get current year and previous year citations for trend calculation
            current_year_citations = 0
            previous_year_citations = 0
            
            for data_point in yearly_data:
                if data_point['year'] == current_year:
                    current_year_citations = data_point['citations']
                elif data_point['year'] == current_year - 1:
                    previous_year_citations = data_point['citations']
            
            # Calculate trend
            citation_trend = None
            if previous_year_citations > 0:
                trend_percentage = round(((current_year_citations - previous_year_citations) / previous_year_citations) * 100, 1)
                citation_trend = {
                    'value': abs(trend_percentage),
                    'isPositive': trend_percentage >= 0
                }
            
            # Calculate average citations per year (excluding years with 0 citations)
            years_with_citations = [dp for dp in yearly_data if dp['citations'] > 0]
            avg_citations_per_year = round(total_citations / len(years_with_citations)) if years_with_citations else 0
            
            # Get h-index approximation (simplified: number of publications with at least N citations)
            # This is a rough approximation since we don't have per-publication citation counts
            h_index_approx = min(citation_analysis['publications_with_citations'], 
                               int(total_citations / max(citation_analysis['publications_with_citations'], 1)))
            
            return {
                'total_citations': total_citations,
                'citation_trend': citation_trend,
                'avg_citations_per_year': avg_citations_per_year,
                'h_index_approximation': h_index_approx,
                'publications_count': citation_analysis['total_publications'],
                'cited_publications_count': citation_analysis['publications_with_citations'],
                'citation_chart_data': yearly_data,
                'analysis_success': citation_analysis.get('error') is None
            }
            
        except Exception as e:
            print(f"Error getting citation metrics: {e}")
            # Return empty metrics on error
            return {
                'total_citations': 0,
                'citation_trend': None,
                'avg_citations_per_year': 0,
                'h_index_approximation': 0,
                'publications_count': 0,
                'cited_publications_count': 0,
                'citation_chart_data': [],
                'analysis_success': False,
                'error': str(e)
            }
