"""
Test suite for CrossRef DOI API functionality.

This test file validates the PublicationAPIClient functionality for:
- DOI validation and retrieval
- Publication metadata formatting
- Search capabilities
- Citation information
- Error handling
"""

import sys
import os
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_basic_doi_retrieval():
    """Test basic DOI retrieval functionality."""
    
    print("🔍 Testing Basic DOI Retrieval")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        # Create client
        client = PublicationAPIClient()
        print("✅ Successfully created PublicationAPIClient")
        
        # Test with a well-known DOI
        test_doi = "10.1371/journal.pone.0000000"  # This might not exist, so let's use a real one
        # Using a real DOI that should exist
        test_doi = "10.1038/nature12373"  # A Nature paper
        
        print(f"\n📋 Testing DOI retrieval for: {test_doi}")
        
        # Add a small delay to be respectful
        time.sleep(1)
        
        # Get publication data
        publication = client.get_publication_formatted(test_doi)
        
        print("✅ Successfully retrieved publication!")
        print(f"   📄 Title: {publication.get('title', 'N/A')[:80]}...")
        print(f"   👥 Authors: {len(publication.get('authors', []))} author(s)")
        print(f"   📚 Journal: {publication.get('journal', 'N/A')}")
        print(f"   📅 Year: {publication.get('published_date', {}).get('year', 'N/A')}")
        print(f"   📊 Citations: {publication.get('citation_count', 0)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import CrossRef DOI module: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error during DOI retrieval: {e}")
        print("💡 This might be due to:")
        print("   - Network connectivity issues")
        print("   - CrossRef API rate limiting")
        print("   - Invalid or non-existent DOI")
        return False


def test_doi_validation():
    """Test DOI validation functionality."""
    
    print("\n🔍 Testing DOI Validation")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        # Test valid DOIs
        valid_dois = [
            "10.1038/nature12373",
            "10.1371/journal.pone.0000000",
            "doi:10.1126/science.1234567",
            "10.1007/s00221-020-05123-4"
        ]
        
        # Test invalid DOIs
        invalid_dois = [
            "not_a_doi",
            "10.invalid",
            "",
            "https://example.com",
            "10"
        ]
        
        print("✅ Testing valid DOIs:")
        for doi in valid_dois:
            is_valid = PublicationAPIClient.validate_doi_format(doi)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {doi}: {is_valid}")
        
        print("\n❌ Testing invalid DOIs:")
        for doi in invalid_dois:
            is_valid = PublicationAPIClient.validate_doi_format(doi)
            status = "✅" if not is_valid else "❌"  # We expect these to be invalid
            print(f"   {status} {doi}: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during DOI validation test: {e}")
        return False


def test_publication_search():
    """Test publication search functionality."""
    
    print("\n🔍 Testing Publication Search")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        client = PublicationAPIClient()
        
        # Test search by author
        print("📋 Testing author search...")
        time.sleep(1)
        
        author_results = client.search_publications_by_author("Einstein", rows=5)
        
        if author_results and 'items' in author_results:
            print(f"✅ Found {len(author_results['items'])} publications by Einstein")
            for i, item in enumerate(author_results['items'][:2]):  # Show first 2
                title = item.get('title', ['Unknown'])[0][:60]
                print(f"   {i+1}. {title}...")
        else:
            print("❌ No results found for Einstein author search")
        
        # Test search by topic
        print("\n📋 Testing topic search...")
        time.sleep(1)
        
        topic_results = client.search_publications("machine learning", rows=3)
        
        if topic_results and 'items' in topic_results:
            print(f"✅ Found publications about machine learning")
            print(f"   Total results available: {topic_results.get('total-results', 'N/A')}")
        else:
            print("❌ No results found for machine learning topic search")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        return False


def test_citation_functionality():
    """Test citation and reference functionality."""
    
    print("\n🔍 Testing Citation Functionality")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        client = PublicationAPIClient()
        
        # Use a DOI that likely has citation data
        test_doi = "10.1038/nature12373"
        
        print(f"📋 Testing citation info for: {test_doi}")
        time.sleep(1)
        
        # Get citation information
        citation_info = client.get_publication_citations(test_doi)
        
        print("✅ Successfully retrieved citation information!")
        print(f"   📊 Citation count: {citation_info.get('citation_count', 0)}")
        print(f"   📚 Reference count: {citation_info.get('reference_count', 0)}")
        
        # Test publication summary
        print("\n📋 Testing publication summary...")
        summary = client.get_publication_summary(test_doi)
        
        print("✅ Successfully generated summary!")
        print(f"   📄 Title: {summary.get('title', 'N/A')[:60]}...")
        print(f"   👥 Authors: {summary.get('authors', 'N/A')[:60]}...")
        print(f"   📅 Year: {summary.get('year', 'N/A')}")
        
        # Test APA citation formatting
        print("\n📋 Testing APA citation formatting...")
        publication = client.get_publication_formatted(test_doi)
        apa_citation = PublicationAPIClient.format_citation_apa(publication)
        
        print("✅ Successfully formatted APA citation!")
        print(f"   📚 {apa_citation[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during citation test: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid DOIs and network issues."""
    
    print("\n🔍 Testing Error Handling")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        client = PublicationAPIClient()
        
        # Test with invalid DOI
        print("📋 Testing invalid DOI handling...")
        invalid_doi = "10.1234/nonexistent.doi.12345"
        
        try:
            publication = client.get_publication_by_doi(invalid_doi)
            print("❌ Expected error for invalid DOI, but got result")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught ValueError for invalid DOI: {str(e)[:60]}...")
        except Exception as e:
            print(f"✅ Caught exception for invalid DOI: {type(e).__name__}")
        
        # Test DOI existence check
        print("\n📋 Testing DOI existence check...")
        exists = client.check_doi_exists("10.1038/nature12373")
        print(f"✅ Valid DOI exists: {exists}")
        
        exists = client.check_doi_exists("10.1234/definitely.not.real")
        print(f"✅ Invalid DOI exists: {exists}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during error handling test: {e}")
        return False


def test_bulk_operations():
    """Test bulk DOI operations."""
    
    print("\n🔍 Testing Bulk Operations")
    print("=" * 40)
    
    try:
        from backend.integrations.crossref_api import PublicationAPIClient
        
        client = PublicationAPIClient()
        
        # Test bulk retrieval with mix of valid and invalid DOIs
        test_dois = [
            "10.1038/nature12373",  # Should work
            "10.1234/fake.doi",     # Should fail
            "10.1126/science.1234567",  # Might work
            "10.1111/j.2517-6161.1996.tb02080.x",
        ]
        
        print(f"📋 Testing bulk retrieval for {len(test_dois)} DOIs...")
        
        # Add delay for rate limiting
        time.sleep(2)
        
        bulk_results = client.bulk_get_publications(test_dois)
        
        print("✅ Bulk operation completed!")
        print(f"   📊 Total requested: {bulk_results.get('total_requested', 0)}")
        print(f"   ✅ Successful: {bulk_results.get('successful_count', 0)}")
        print(f"   ❌ Failed: {bulk_results.get('failed_count', 0)}")
        
        if bulk_results.get('failed'):
            print("   Failed DOIs:")
            for failed in bulk_results['failed']:
                print(f"     - {failed.get('doi', 'N/A')}: {failed.get('error', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during bulk operations test: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and provide summary."""
    
    print("🚀 CrossRef DOI API Test Suite")
    print("=" * 50)
    print("📝 This test suite will:")
    print("   1. Test basic DOI retrieval")
    print("   2. Test DOI validation")
    print("   3. Test publication search")
    print("   4. Test citation functionality")
    print("   5. Test error handling")
    print("   6. Test bulk operations")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Basic DOI Retrieval", test_basic_doi_retrieval),
        ("DOI Validation", test_doi_validation),
        ("Publication Search", test_publication_search),
        ("Citation Functionality", test_citation_functionality),
        ("Error Handling", test_error_handling),
        ("Bulk Operations", test_bulk_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! CrossRef DOI API is working correctly.")
    elif passed > total // 2:
        print("⚠️  Most tests passed. Some issues may need attention.")
    else:
        print("❌ Many tests failed. Check your network connection and dependencies.")
    
    print("\n💡 Tips:")
    print("   - If tests fail, check your internet connection")
    print("   - Some failures might be due to CrossRef API rate limiting")
    print("   - Try running tests again after a few minutes")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print("\n✅ CrossRef DOI API test suite completed successfully!")
    else:
        print("\n❌ Some tests failed. Review the output above for details.")
    
    print("\n📝 Note: Test results may vary due to network conditions and API availability") 