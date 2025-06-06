#!/usr/bin/env python3
"""
Test script for ORCID User Identity Information extraction
Tests the get_user_identity_info() method with real ORCID IDs
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.integrations.orcid_api import ORCIDAPIClient

def test_user_identity_info():
    """Test the get_user_identity_info() method with different ORCID IDs"""
    
    # Test ORCID IDs - mix of different profiles for comprehensive testing
    test_orcid_ids = [
        "0009-0007-8094-7155",  # Our working test ID
        "0000-0002-1825-0097",  # Another test ID from documentation
        "0000-0003-1574-0784",  # Another example ID
    ]
    
    print("🧪 Testing ORCID User Identity Information Extraction")
    print("=" * 70)
    print()
    
    for i, orcid_id in enumerate(test_orcid_ids, 1):
        print(f"📋 Test {i}: ORCID ID {orcid_id}")
        print("-" * 50)
        
        try:
            # Initialize client (no access token needed for public data)
            client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
            
            # Get user identity information
            user_info = client.get_user_identity_info()
            
            # Display results
            print("✅ User Identity Information Retrieved:")
            print(f"   🆔 ORCID ID: {user_info.get('orcid_id', 'N/A')}")
            print(f"   👤 Name: {user_info.get('name', 'N/A')}")
            print(f"   📧 Email: {user_info.get('email', 'Not public/available')}")
            print(f"   🏢 Current Affiliation: {user_info.get('current_affiliation', 'N/A')}")
            print(f"   📍 Current Location: {user_info.get('current_location', 'N/A')}")
            print(f"   🔗 Profile URL: {user_info.get('profile_url', 'N/A')}")
            
            if 'error' in user_info:
                print(f"   ⚠️  Error: {user_info['error']}")
            
        except Exception as e:
            print(f"❌ Error testing ORCID ID {orcid_id}: {str(e)}")
        
        print()

def test_user_identity_edge_cases():
    """Test edge cases for user identity information"""
    
    print("🧪 Testing Edge Cases for User Identity")
    print("=" * 50)
    print()
    
    # Test cases with potential issues
    edge_cases = [
        {
            'name': 'Invalid ORCID ID Format',
            'orcid_id': 'invalid-orcid-format',
            'should_fail': True
        },
        {
            'name': 'Non-existent ORCID ID',
            'orcid_id': '0000-0000-0000-0000',
            'should_fail': True
        },
        {
            'name': 'ORCID ID with URI prefix',
            'orcid_id': 'https://orcid.org/0009-0007-8094-7155',
            'should_fail': False
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"📋 Edge Case {i}: {test_case['name']}")
        print(f"   Testing ORCID ID: {test_case['orcid_id']}")
        
        try:
            client = ORCIDAPIClient(access_token="", orcid_id=test_case['orcid_id'])
            user_info = client.get_user_identity_info()
            
            if test_case['should_fail']:
                print(f"   ⚠️  Expected failure but got result: {user_info.get('name', 'N/A')}")
                if 'error' in user_info:
                    print(f"   ✅ Graceful error handling: {user_info['error']}")
            else:
                print(f"   ✅ Success: {user_info.get('name', 'N/A')}")
                
        except Exception as e:
            if test_case['should_fail']:
                print(f"   ✅ Expected error: {str(e)}")
            else:
                print(f"   ❌ Unexpected error: {str(e)}")
        
        print()

def test_individual_endpoints():
    """Test the individual endpoints used by get_user_identity_info()"""
    
    print("🧪 Testing Individual Endpoints")
    print("=" * 40)
    print()
    
    test_orcid_id = "0009-0007-8094-7155"
    
    try:
        client = ORCIDAPIClient(access_token="", orcid_id=test_orcid_id)
        
        # Test personal details endpoint
        print("📋 Testing /personal-details endpoint...")
        try:
            personal_details = client.get_personal_details()
            name_info = personal_details.get('name', {})
            print(f"   ✅ Personal details retrieved")
            print(f"   👤 Given names: {name_info.get('given-names', {}).get('value', 'N/A')}")
            print(f"   👤 Family name: {name_info.get('family-name', {}).get('value', 'N/A')}")
            if name_info.get('credit-name'):
                print(f"   📝 Credit name: {name_info['credit-name'].get('value', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        print()
        
        # Test emails endpoint
        print("📋 Testing /emails endpoint...")
        try:
            emails_data = client.get_emails()
            emails = emails_data.get('email', [])
            print(f"   ✅ Found {len(emails)} email(s)")
            for email in emails:
                primary = "✅ PRIMARY" if email.get('primary') else ""
                print(f"   📧 {email.get('email', 'N/A')} {primary}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        print()
        
        # Test employments endpoint
        print("📋 Testing /employments endpoint...")
        try:
            employments = client.get_researcher_employments()
            groups = employments.get('affiliation-group', [])
            print(f"   ✅ Found {len(groups)} employment group(s)")
            
            # Look for current employment
            current_found = False
            for group in groups:
                for summary in group.get('summaries', []):
                    if not summary.get('end-date'):  # Current employment
                        org = summary.get('organization', {})
                        print(f"   🏢 Current: {org.get('name', 'N/A')}")
                        address = org.get('address', {})
                        if address:
                            location_parts = [
                                address.get('city', ''),
                                address.get('region', ''),
                                address.get('country', '')
                            ]
                            location = ', '.join([p for p in location_parts if p])
                            if location:
                                print(f"   📍 Location: {location}")
                        current_found = True
                        break
                if current_found:
                    break
            
            if not current_found:
                print("   ℹ️  No current employment found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")

def test_json_output():
    """Test JSON serialization of user identity data"""
    
    print("🧪 Testing JSON Output")
    print("=" * 30)
    print()
    
    test_orcid_id = "0009-0007-8094-7155"
    
    try:
        client = ORCIDAPIClient(access_token="", orcid_id=test_orcid_id)
        user_info = client.get_user_identity_info()
        
        # Test JSON serialization
        json_output = json.dumps(user_info, indent=2, ensure_ascii=False)
        print("✅ JSON serialization successful:")
        print(json_output)
        
        # Test JSON parsing
        parsed_data = json.loads(json_output)
        print(f"\n✅ JSON parsing successful. Keys: {list(parsed_data.keys())}")
        
    except Exception as e:
        print(f"❌ JSON processing error: {str(e)}")
    
    print()

def main():
    """Run all tests"""
    
    print("🚀 ORCID User Identity Information Test Suite")
    print("=" * 80)
    print()
    
    # Run all test functions
    test_user_identity_info()
    test_user_identity_edge_cases()
    test_individual_endpoints()
    test_json_output()
    
    print("🎉 All tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    main() 