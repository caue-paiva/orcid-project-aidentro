#!/usr/bin/env python3
"""
Test script for ORCIDAPIClient with hardcoded ORCID ID: 0009-0007-8094-7155
"""

import sys
import os

# Add the src/backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', '..', 'src', 'backend')
sys.path.insert(0, backend_dir)

from orcid_utils import ORCIDAPIClient
import json

def test_orcid_client():
    """Test the ORCIDAPIClient with a hardcoded ORCID ID"""
    
    # Hardcoded test data
    test_orcid_id = "0009-0007-8094-7155"
    # For public API calls, we can use an empty token or None
    test_access_token = ""  # Empty token for public API
    
    print(f"🧪 Testing ORCIDAPIClient with ORCID ID: {test_orcid_id}")
    print("📋 Using Public API (no access token required)")
    print("=" * 60)
    
    try:
        # Initialize the client
        print("📋 Initializing ORCID API Client...")
        client = ORCIDAPIClient(access_token=test_access_token, orcid_id=test_orcid_id)
        print(f"✅ Client initialized successfully for ORCID ID: {client.orcid_id}")
        print()
        
        # Test 1: Validate ORCID ID format
        print("🔍 Test 1: Validating ORCID ID format...")
        is_valid = ORCIDAPIClient.validate_orcid_id_format(test_orcid_id)
        print(f"ORCID ID {test_orcid_id} is valid: {is_valid}")
        print()
        
        # Test 2: Get basic person information
        print("👤 Test 2: Getting person information...")
        try:
            person_info = client.get_researcher_person_info()
            name = person_info.get('name', {})
            given_names = name.get('given-names', {}).get('value', 'Unknown') if name.get('given-names') else 'Unknown'
            family_name = name.get('family-name', {}).get('value', 'Unknown') if name.get('family-name') else 'Unknown'
            print(f"✅ Name: {given_names} {family_name}")
            
            # Print keywords if available
            keywords = person_info.get('keywords', {}).get('keyword', [])
            if keywords:
                keyword_values = [kw.get('content', 'Unknown') for kw in keywords]
                print(f"🏷️  Keywords: {', '.join(keyword_values)}")
            else:
                print("🏷️  No keywords found")
        except Exception as e:
            print(f"❌ Error getting person info: {e}")
        print()
        
        # Test 3: Get complete record
        print("📖 Test 3: Getting complete record...")
        try:
            record = client.get_researcher_record()
            print(f"✅ Complete record retrieved (keys: {list(record.keys())})")
        except Exception as e:
            print(f"❌ Error getting complete record: {e}")
        print()
        
        # Test 4: Get works
        print("📚 Test 4: Getting works...")
        try:
            works = client.get_researcher_works()
            works_count = len(works.get('group', []))
            print(f"✅ Found {works_count} work groups")
            
            # Get formatted works for CV
            cv_works = client.get_researcher_works_for_cv()
            print(f"📄 Formatted {len(cv_works)} works for CV")
            
            # Show first few works
            for i, work in enumerate(cv_works[:3]):
                print(f"   {i+1}. {work.get('title', 'Unknown Title')} ({work.get('type', 'Unknown Type')})")
        except Exception as e:
            print(f"❌ Error getting works: {e}")
        print()
        
        # Test 5: Get employments
        print("💼 Test 5: Getting employments...")
        try:
            employments = client.get_researcher_employments()
            emp_count = len(employments.get('affiliation-group', []))
            print(f"✅ Found {emp_count} employment groups")
        except Exception as e:
            print(f"❌ Error getting employments: {e}")
        print()
        
        # Test 6: Get education
        print("🎓 Test 6: Getting education...")
        try:
            education = client.get_researcher_education()
            edu_count = len(education.get('affiliation-group', []))
            print(f"✅ Found {edu_count} education groups")
        except Exception as e:
            print(f"❌ Error getting education: {e}")
        print()
        
        # Test 7: Get funding
        print("💰 Test 7: Getting funding...")
        try:
            funding = client.get_researcher_funding()
            funding_count = len(funding.get('group', []))
            print(f"✅ Found {funding_count} funding groups")
        except Exception as e:
            print(f"❌ Error getting funding: {e}")
        print()
        
        # Test 8: Get comprehensive summary
        print("📊 Test 8: Getting comprehensive summary...")
        try:
            summary = client.get_researcher_summary(include_all_sections=False)
            print(f"✅ Summary generated with {len(summary)} sections")
            print(f"   - Works: {summary.get('works_count', 0)}")
            print(f"   - Employments: {summary.get('employments_count', 0)}")
            print(f"   - Education: {summary.get('education_count', 0)}")
            print(f"   - Funding: {summary.get('funding_count', 0)}")
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
        print()
        
        # Test 9: Get CV-formatted affiliations
        print("📋 Test 9: Getting CV-formatted affiliations...")
        try:
            affiliations = client.get_researcher_affiliations_for_cv()
            emp_count = len(affiliations.get('employment', []))
            edu_count = len(affiliations.get('education', []))
            print(f"✅ CV affiliations: {emp_count} employment, {edu_count} education entries")
        except Exception as e:
            print(f"❌ Error getting CV affiliations: {e}")
        print()
        
        # Test 10: Search functionality
        print("🔍 Test 10: Testing search functionality...")
        try:
            # Search by name
            search_results = client.search_researchers_by_name(given_name="John", family_name="Smith")
            print(f"✅ Name search returned {len(search_results)} results")
            
            # Advanced search
            advanced_results = client.search_researchers_advanced(keyword="machine learning")
            print(f"✅ Advanced search returned {len(advanced_results)} results")
        except Exception as e:
            print(f"❌ Error in search: {e}")
        print()
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Failed to initialize client or run tests: {e}")
        print("💡 Error details: {str(e)}")

def test_without_token():
    """Test what we can do without an access token"""
    print("\n" + "=" * 60)
    print("🧪 Testing without access token (validation only)")
    print("=" * 60)
    
    test_orcid_id = "0009-0007-8094-7155"
    
    # Test ORCID ID validation
    is_valid = ORCIDAPIClient.validate_orcid_id_format(test_orcid_id)
    print(f"✅ ORCID ID {test_orcid_id} format validation: {is_valid}")
    
    # Test invalid ORCID IDs
    invalid_ids = [
        "invalid-id",
        "0000-0000-0000-000",  # Too short
        "0000-0000-0000-00000",  # Too long
        "abcd-efgh-ijkl-mnop",  # Non-numeric
        ""  # Empty
    ]
    
    print("\n🔍 Testing invalid ORCID ID formats:")
    for invalid_id in invalid_ids:
        is_valid = ORCIDAPIClient.validate_orcid_id_format(invalid_id)
        print(f"   {invalid_id or '(empty)'}: {is_valid}")

if __name__ == "__main__":
    print("🚀 Starting ORCID API Client Tests")
    print("=" * 60)
    
    # Test validation without token first
    test_without_token()
    
    # Test with Public API (no token needed)
    print("\n" + "=" * 60)
    print("🔓 Testing Public API calls (no access token required)")
    print("=" * 60)
    
    # Run the full test with public API
    test_orcid_client() 