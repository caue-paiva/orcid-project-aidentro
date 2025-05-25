"""
ORCID API utility functions.

This module provides helper functions for interacting with the ORCID Public API
using access tokens obtained through the OAuth flow.
"""

import requests
import json
from typing import Dict, List, Optional, Union
from decouple import config


class ORCIDAPIClient:
    """Client for interacting with ORCID Public API"""
    
    def __init__(self, access_token: str, base_url: str = None):
        """
        Initialize ORCID API client.
        
        Args:
            access_token: Valid ORCID access token
            base_url: ORCID base URL (defaults to config value)
        """
        self.access_token = access_token
        self.base_url = base_url or config('ORCID_BASE_URL', default='https://sandbox.orcid.org')
        
        # Convert to public API URL
        if 'sandbox.orcid.org' in self.base_url:
            self.api_base_url = 'https://pub.sandbox.orcid.org/v3.0'
        else:
            self.api_base_url = 'https://pub.orcid.org/v3.0'
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
    
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
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_record(self, orcid_id: str) -> Dict:
        """
        Get a researcher's complete public record.
        
        Args:
            orcid_id: ORCID identifier (e.g., '0000-0001-2345-6789')
            
        Returns:
            Complete ORCID record dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_person_info(self, orcid_id: str) -> Dict:
        """
        Get a researcher's personal information (names, keywords, etc.).
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Person information dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/person"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_works(self, orcid_id: str) -> Dict:
        """
        Get a researcher's works (publications, datasets, etc.).
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Works summary dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/works"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_employments(self, orcid_id: str) -> Dict:
        """
        Get a researcher's employment history.
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Employment history dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/employments"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_education(self, orcid_id: str) -> Dict:
        """
        Get a researcher's education history.
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Education history dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/educations"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_researcher_funding(self, orcid_id: str) -> Dict:
        """
        Get a researcher's funding information.
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Funding information dictionary
        """
        clean_orcid_id = self._clean_orcid_id(orcid_id)
        url = f"{self.api_base_url}/{clean_orcid_id}/fundings"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
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


def search_researchers_by_name(access_token: str, given_name: str = None, 
                              family_name: str = None, **kwargs) -> List[Dict]:
    """
    Search for researchers by name.
    
    Args:
        access_token: Valid ORCID access token
        given_name: Given name to search for
        family_name: Family name to search for
        **kwargs: Additional search parameters
        
    Returns:
        List of researcher records
    """
    client = ORCIDAPIClient(access_token)
    
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
    
    results = client.search_researchers(query)
    return results.get('result', [])


def search_researchers_by_affiliation(access_token: str, organization: str, 
                                     **kwargs) -> List[Dict]:
    """
    Search for researchers by affiliation.
    
    Args:
        access_token: Valid ORCID access token
        organization: Organization name to search for
        **kwargs: Additional search parameters
        
    Returns:
        List of researcher records
    """
    client = ORCIDAPIClient(access_token)
    
    query = f'affiliation-org-name:"{organization}"'
    
    # Add additional search parameters
    for key, value in kwargs.items():
        if value:
            query += f' AND {key}:"{value}"'
    
    results = client.search_researchers(query)
    return results.get('result', [])


def get_researcher_summary(access_token: str, orcid_id: str) -> Dict:
    """
    Get a comprehensive summary of a researcher's profile.
    
    Args:
        access_token: Valid ORCID access token
        orcid_id: ORCID identifier
        
    Returns:
        Researcher summary dictionary with person info, works, employments, etc.
    """
    client = ORCIDAPIClient(access_token)
    
    try:
        # Get basic person information
        person_info = client.get_researcher_person_info(orcid_id)
        
        # Get works summary
        try:
            works = client.get_researcher_works(orcid_id)
        except:
            works = {'group': []}
        
        # Get employment history
        try:
            employments = client.get_researcher_employments(orcid_id)
        except:
            employments = {'affiliation-group': []}
        
        # Get education history
        try:
            education = client.get_researcher_education(orcid_id)
        except:
            education = {'affiliation-group': []}
        
        # Build summary
        summary = {
            'orcid_id': orcid_id,
            'person': person_info,
            'works_count': len(works.get('group', [])),
            'works': works,
            'employments_count': len(employments.get('affiliation-group', [])),
            'employments': employments,
            'education_count': len(education.get('affiliation-group', [])),
            'education': education
        }
        
        return summary
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch researcher summary: {e}")


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


# Example usage functions
def example_search_and_get_profile(access_token: str):
    """
    Example function showing how to search for researchers and get their profiles.
    """
    print("🔍 Searching for researchers named 'Smith'...")
    
    # Search for researchers
    results = search_researchers_by_name(access_token, family_name="Smith")
    
    print(f"Found {len(results)} researchers")
    
    if results:
        # Get detailed profile for first result
        first_result = results[0]
        orcid_id = first_result['orcid-identifier']['path']
        
        print(f"\n📋 Getting profile for ORCID iD: {orcid_id}")
        
        summary = get_researcher_summary(access_token, orcid_id)
        
        # Extract name
        person = summary['person']
        name = person.get('name', {})
        given_names = name.get('given-names', {}).get('value', 'Unknown')
        family_name = name.get('family-name', {}).get('value', 'Unknown')
        
        print(f"Name: {given_names} {family_name}")
        print(f"Works: {summary['works_count']}")
        print(f"Employments: {summary['employments_count']}")
        print(f"Education: {summary['education_count']}")
        
        return summary
    
    return None 