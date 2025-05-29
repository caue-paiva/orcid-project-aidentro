"""
ORCID API utility functions.

This module provides helper functions for interacting with the ORCID Public API
using access tokens obtained through the OAuth flow.
"""

import requests
import json
from typing import Dict, List, Optional, Union
from decouple import config
import urllib3


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

