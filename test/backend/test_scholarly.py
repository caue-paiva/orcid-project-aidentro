#!/usr/bin/env python3
"""
Simple test to verify scholarly library works by searching for Geoffrey Hinton.
"""

import time

def test_scholarly_search():
    """Test importing scholarly and searching for Geoffrey Hinton."""
    
    print("🔍 Testing Scholarly Library - Basic Search")
    print("=" * 40)
    
    try:
        # Try to import scholarly
        print("📋 Step 1: Importing scholarly library...")
        from scholarly import scholarly
        print("✅ Successfully imported scholarly")
        
        # Try a simple search
        print("\n📋 Step 2: Searching for 'Geoffrey Hinton'...")
        
        # Add a small delay to be respectful
        time.sleep(2)
        
        # Search for the author
        search_query = scholarly.search_author('Marty Banks, Berkeley')
        
        # Get the first result
        author = next(search_query, None)
        
        if author:
            print("✅ Search successful!")
            print(f"   👤 Found author: {author.get('name', 'Unknown')}")
            print(f"   🏢 Affiliation: {author.get('affiliation', 'Not provided')}")
            print(f"   🆔 Scholar ID: {author.get('scholar_id', 'Not provided')}")
            
            print("\n🎉 Basic search test passed!")
            return True
        
        else:
            print("❌ No results found for 'Geoffrey Hinton'")
            print("   This might be due to rate limiting or network issues")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import scholarly: {e}")
        print("💡 Please install the scholarly library:")
        print("   pip install scholarly")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 This might be due to:")
        print("   - Network connectivity issues")
        print("   - Google Scholar rate limiting")
        print("   - Firewall blocking requests")
        return False


if __name__ == "__main__":
    print("🚀 Simple Scholarly Search Test")
    print("=" * 30)
    print("📝 This test will:")
    print("   1. Import the scholarly library")
    print("   2. Search for 'Geoffrey Hinton'")
    print("   3. Show basic search results")
    print("=" * 30)
    
    success = test_scholarly_search()
    
    print("\n" + "=" * 30)
    if success:
        print("✅ Test completed successfully!")
        print("💡 The scholarly library is working and can search Google Scholar")
    else:
        print("❌ Test failed!")
        print("💡 Check your internet connection and try:")
        print("   pip install scholarly")
    
    print("\n📝 Note: If you get rate limited, try running the test again later")
