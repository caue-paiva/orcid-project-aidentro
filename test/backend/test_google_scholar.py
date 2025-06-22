#!/usr/bin/env python3
"""
Test script for Google Scholar API integration.

This script demonstrates how to use the Google Scholar API to get citation metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.integrations.google_scholar import (
    GoogleScholarAPI, 
    get_author_citations_by_year,
    get_author_citations_for_years,
    get_cumulative_citations,
    get_complete_author_metrics
)


def test_basic_import():
    """Test if we can import and initialize the Google Scholar API."""
    print("🔍 Testing Basic Import and Initialization")
    print("=" * 45)
    
    try:
        api = GoogleScholarAPI(delay=1.0)
        print("✅ Successfully imported and initialized GoogleScholarAPI")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Please install the scholarly library: pip install scholarly")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_simple_search():
    """Test a simple author search."""
    print("\n🔍 Testing Simple Author Search")
    print("=" * 35)
    
    try:
        api = GoogleScholarAPI(delay=3.0)  # Longer delay to be respectful
        
        # Test with a very famous researcher
        test_author = "Geoffrey Hinton"
        print(f"📋 Searching for '{test_author}'...")
        
        result = api.search_author(test_author)
        
        if result:
            print(f"✅ Search successful!")
            print(f"   👤 Found: {result.get('name', 'Unknown')}")
            print(f"   🏢 Affiliation: {result.get('affiliation', 'Not provided')}")
            print(f"   📊 Total Citations: {result.get('total_citations', 0):,}")
            print(f"   📈 H-Index: {result.get('h_index', 0)}")
            print(f"   📉 i10-Index: {result.get('i10_index', 0)}")
            return True
        else:
            print("⚠️  Search returned no results")
            print("   This might be due to Google Scholar rate limiting")
            return False
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        print("💡 This might be due to:")
        print("   - Google Scholar rate limiting")
        print("   - Network connectivity issues")
        print("   - Missing 'scholarly' library")
        return False


def test_citation_metrics():
    """Test citation metrics functionality."""
    print("\n📊 Testing Citation Metrics")
    print("=" * 30)
    
    try:
        api = GoogleScholarAPI(delay=3.0)
        test_author = "Geoffrey Hinton"
        
        print(f"📋 Getting citation data for '{test_author}'...")
        
        # Test getting citations for a specific year
        citations_2023 = api.get_citations_by_year(test_author, 2023)
        if citations_2023 is not None:
            print(f"✅ Citations in 2023: {citations_2023:,}")
        else:
            print("⚠️  No 2023 citation data available")
        
        # Test getting citations for multiple years
        years = [2021, 2022, 2023]
        citations_by_years = api.get_citations_for_years(test_author, years)
        
        if citations_by_years:
            print(f"✅ Citations by year:")
            for year, citations in sorted(citations_by_years.items()):
                print(f"   {year}: {citations:,} citations")
            return True
        else:
            print("⚠️  No multi-year citation data available")
            return False
            
    except Exception as e:
        print(f"❌ Citation metrics test failed: {e}")
        return False


def test_convenience_functions():
    """Test the convenience functions."""
    print("\n🛠️  Testing Convenience Functions")
    print("=" * 35)
    
    try:
        test_author = "Geoffrey Hinton"
        
        print(f"📋 Testing convenience functions for '{test_author}'...")
        
        # Test single year convenience function
        citations_2023 = get_author_citations_by_year(test_author, 2023)
        if citations_2023 is not None:
            print(f"✅ Convenience function (single year): {citations_2023:,} citations in 2023")
        else:
            print("⚠️  Single year convenience function returned no data")
        
        # Test multiple years convenience function
        citations_years = get_author_citations_for_years(test_author, [2022, 2023])
        if citations_years:
            print(f"✅ Convenience function (multiple years): {citations_years}")
            return True
        else:
            print("⚠️  Multiple years convenience function returned no data")
            return False
            
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False


def test_google_scholar_functionality():
    """Test Google Scholar API functionality with a well-known researcher."""
    
    print("🔍 Testing Google Scholar API Integration")
    print("=" * 50)
    
    # Use a well-known researcher for testing
    test_author = "Andrew Ng"  # Famous AI researcher with many publications
    test_affiliation = "Stanford University"
    
    try:
        # Initialize API client
        api = GoogleScholarAPI(delay=4.0)  # Longer delay to be respectful
        print(f"✅ Google Scholar API client initialized")
        
        # Test 1: Search for author
        print(f"\n📋 Test 1: Searching for author '{test_author}'")
        author_data = api.search_author(test_author, test_affiliation)
        
        if author_data:
            print(f"✅ Found author: {author_data.get('name', 'Unknown')}")
            print(f"   📧 Email: {author_data.get('email', 'Not provided')}")
            print(f"   🏢 Affiliation: {author_data.get('affiliation', 'Not provided')}")
            print(f"   📊 Total Citations: {author_data.get('total_citations', 0):,}")
            print(f"   📈 H-Index: {author_data.get('h_index', 0)}")
            print(f"   📉 i10-Index: {author_data.get('i10_index', 0)}")
            
            # Show recent years' citations
            citations_per_year = author_data.get('citations_per_year', {})
            recent_years = sorted([year for year in citations_per_year.keys() if year >= 2020])[-5:]
            if recent_years:
                print(f"   📅 Recent citations:")
                for year in recent_years:
                    print(f"      {year}: {citations_per_year[year]:,} citations")
        else:
            print(f"❌ Could not find author '{test_author}'")
            print("   Skipping remaining tests due to search failure")
            return False
        
        # Test 2: Get citations for specific year
        print(f"\n📋 Test 2: Getting citations for 2023")
        citations_2023 = api.get_citations_by_year(test_author, 2023, test_affiliation)
        
        if citations_2023 is not None:
            print(f"✅ Citations in 2023: {citations_2023:,}")
        else:
            print(f"⚠️  Could not get citations for 2023")
        
        # Test 3: Get citations for multiple years
        print(f"\n📋 Test 3: Getting citations for multiple years (2020-2023)")
        years = [2020, 2021, 2022, 2023]
        citations_by_years = api.get_citations_for_years(test_author, years, test_affiliation)
        
        if citations_by_years:
            print(f"✅ Citations by year:")
            for year, citations in sorted(citations_by_years.items()):
                print(f"   {year}: {citations:,} citations")
        else:
            print(f"⚠️  Could not get citations for multiple years")
        
        # Test 4: Get cumulative citations
        print(f"\n📋 Test 4: Getting cumulative citations (2020-2023)")
        cumulative_data = api.get_cumulative_citations(test_author, years, test_affiliation)
        
        if cumulative_data:
            print(f"✅ Cumulative citations:")
            for data in cumulative_data:
                print(f"   {data.year}: {data.citations:,} new, {data.cumulative_citations:,} total")
        else:
            print(f"⚠️  Could not get cumulative citation data")
        
        # Test 5: Get complete author metrics
        print(f"\n📋 Test 5: Getting complete author metrics")
        metrics = api.get_author_metrics(test_author, test_affiliation)
        
        if metrics:
            print(f"✅ Complete metrics for {metrics.name}:")
            print(f"   🆔 Scholar ID: {metrics.scholar_id}")
            print(f"   📊 Total Citations: {metrics.total_citations:,}")
            print(f"   📈 H-Index: {metrics.h_index}")
            print(f"   📉 i10-Index: {metrics.i10_index}")
            print(f"   📚 Publications Count: {metrics.publications_count}")
            
            # Show top citation years
            top_years = sorted(metrics.citations_per_year.items(), 
                             key=lambda x: x[1], reverse=True)[:5]
            if top_years:
                print(f"   🏆 Top citation years:")
                for year, citations in top_years:
                    print(f"      {year}: {citations:,} citations")
        else:
            print(f"⚠️  Could not get complete author metrics")
        
        # Test 6: Test convenience functions
        print(f"\n📋 Test 6: Testing convenience functions")
        
        # Test convenience function for single year
        conv_citations_2023 = get_author_citations_by_year(test_author, 2023, test_affiliation)
        if conv_citations_2023 is not None:
            print(f"✅ Convenience function - 2023 citations: {conv_citations_2023:,}")
        
        # Test convenience function for multiple years
        conv_citations_years = get_author_citations_for_years(test_author, [2022, 2023], test_affiliation)
        if conv_citations_years:
            print(f"✅ Convenience function - Multiple years: {conv_citations_years}")
        
        # Test convenience function for cumulative data
        conv_cumulative = get_cumulative_citations(test_author, [2022, 2023], test_affiliation)
        if conv_cumulative:
            print(f"✅ Convenience function - Cumulative data: {len(conv_cumulative)} data points")
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print(f"💡 Please install the scholarly library: pip install scholarly")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"💡 This might be due to Google Scholar rate limiting or network issues")
        return False


def test_integration_with_orcid():
    """Test integration between Google Scholar and ORCID data."""
    
    print("\n🔗 Testing Google Scholar + ORCID Integration")
    print("=" * 50)
    
    try:
        # Import ORCID client
        from orcid_utils import ORCIDAPIClient
        
        # Test with a researcher who has both ORCID and Google Scholar profiles
        orcid_id = "0000-0003-1574-0784"  # Example ORCID ID
        
        # Get ORCID data
        orcid_client = ORCIDAPIClient("", orcid_id)
        person_info = orcid_client.get_researcher_person_info()
        
        if person_info and 'name' in person_info:
            # Extract name from ORCID
            given_names = person_info['name'].get('given-names', {}).get('value', '')
            family_name = person_info['name'].get('family-name', {}).get('value', '')
            full_name = f"{given_names} {family_name}".strip()
            
            print(f"✅ Found ORCID profile for: {full_name}")
            
            # Search Google Scholar using ORCID name
            scholar_api = GoogleScholarAPI(delay=4.0)
            scholar_data = scholar_api.search_author(full_name)
            
            if scholar_data:
                print(f"✅ Found Google Scholar profile for: {scholar_data.get('name', 'Unknown')}")
                print(f"   📊 Total Citations: {scholar_data.get('total_citations', 0):,}")
                
                # Compare publication counts
                orcid_works = orcid_client.get_researcher_works()
                orcid_works_count = len(orcid_works.get('group', []))
                scholar_pub_count = len(scholar_data.get('publications', []))
                
                print(f"   📚 ORCID Works: {orcid_works_count}")
                print(f"   📚 Scholar Publications: {scholar_pub_count}")
                
                print(f"✅ Successfully integrated ORCID and Google Scholar data!")
                return True
            else:
                print(f"❌ Could not find Google Scholar profile for {full_name}")
                return False
        else:
            print(f"❌ Could not get ORCID person info")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import ORCID utilities: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Google Scholar API Tests")
    print("=" * 60)
    print("📍 Working Directory:", os.getcwd())
    print("📂 Script Location:", __file__)
    
    # Show the import path
    backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend')
    abs_backend_path = os.path.abspath(backend_path)
    print("🐍 Import Path:", abs_backend_path)
    print("=" * 60)
    
    # Run tests in sequence with success tracking
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic import
    total_tests += 1
    if test_basic_import():
        tests_passed += 1
    
    # Test 2: Simple search (only if import works)
    if tests_passed > 0:
        total_tests += 1
        if test_simple_search():
            tests_passed += 1
    
    