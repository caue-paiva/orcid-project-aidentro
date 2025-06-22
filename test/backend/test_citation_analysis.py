#!/usr/bin/env python3
"""
Test script for citation analysis functionality.

This script demonstrates how to use the new citation analysis methods
to get citation data from ORCID and CrossRef APIs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.orcid_api import ORCIDAPIClient
import json

def test_citation_analysis():
    """Test the citation analysis functionality with a sample ORCID ID."""
    
    # Test with a well-known researcher's ORCID ID (example)
    # You can replace this with any valid ORCID ID
    test_orcid_id = "0000-0003-1574-0784"  # Example ORCID ID
    
    print(f"🔍 Testing citation analysis for ORCID ID: {test_orcid_id}")
    print("=" * 60)
    
    try:
        # Initialize ORCID client (no access token needed for public data)
        client = ORCIDAPIClient(access_token="", orcid_id=test_orcid_id)
        
        # Test basic citation analysis
        print("📊 Running citation analysis...")
        citation_analysis = client.get_citation_analysis(years_back=5)
        
        print("\n📈 Citation Analysis Results:")
        print(f"  • Analysis Period: {citation_analysis['analysis_period']}")
        print(f"  • Total Citations: {citation_analysis['total_citations']}")
        print(f"  • Total Publications: {citation_analysis['total_publications']}")
        print(f"  • Publications with Citations: {citation_analysis['publications_with_citations']}")
        print(f"  • Successful API Lookups: {citation_analysis['successful_lookups']}")
        
        if citation_analysis.get('error'):
            print(f"  ⚠️  Error: {citation_analysis['error']}")
        
        print("\n📅 Yearly Citation Data:")
        for data_point in citation_analysis['yearly_data']:
            print(f"  • {data_point['year']}: {data_point['citations']} citations (Cumulative: {data_point['cumulative_citations']})")
        
        # Test dashboard metrics
        print("\n🎯 Testing dashboard metrics...")
        dashboard_metrics = client.get_citation_metrics_for_dashboard()
        
        print("\n📊 Dashboard Metrics:")
        print(f"  • Total Citations: {dashboard_metrics['total_citations']}")
        print(f"  • Average Citations/Year: {dashboard_metrics['avg_citations_per_year']}")
        print(f"  • H-Index Approximation: {dashboard_metrics['h_index_approximation']}")
        print(f"  • Publications Count: {dashboard_metrics['publications_count']}")
        print(f"  • Cited Publications: {dashboard_metrics['cited_publications_count']}")
        print(f"  • Analysis Success: {dashboard_metrics['analysis_success']}")
        
        if dashboard_metrics['citation_trend']:
            trend = dashboard_metrics['citation_trend']
            direction = "↗️" if trend['isPositive'] else "↘️"
            print(f"  • Citation Trend: {direction} {trend['value']}%")
        else:
            print("  • Citation Trend: No trend data available")
        
        if dashboard_metrics.get('error'):
            print(f"  ⚠️  Error: {dashboard_metrics['error']}")
        
        # Save results to JSON for frontend testing
        results = {
            'citation_analysis': citation_analysis,
            'dashboard_metrics': dashboard_metrics
        }
        
        with open('citation_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to 'citation_analysis_results.json'")
        print(f"✅ Citation analysis test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during citation analysis: {e}")
        print(f"   This might be due to:")
        print(f"   - Invalid ORCID ID")
        print(f"   - Network connectivity issues")
        print(f"   - API rate limits")
        print(f"   - Missing publication DOIs in the ORCID record")

def test_with_custom_orcid():
    """Test with a custom ORCID ID provided by user."""
    
    orcid_id = input("Enter an ORCID ID to test (format: 0000-0000-0000-0000): ").strip()
    
    if not orcid_id:
        print("No ORCID ID provided, using default test ID.")
        test_citation_analysis()
        return
    
    # Validate basic format
    if len(orcid_id) != 19 or orcid_id.count('-') != 3:
        print("Invalid ORCID ID format. Expected format: 0000-0000-0000-0000")
        return
    
    try:
        client = ORCIDAPIClient(access_token="", orcid_id=orcid_id)
        
        print(f"🔍 Testing citation analysis for ORCID ID: {orcid_id}")
        print("=" * 60)
        
        # Get basic researcher info first
        user_info = client.get_user_identity_info()
        print(f"👤 Researcher: {user_info['name']}")
        if user_info['current_affiliation']:
            print(f"🏛️  Affiliation: {user_info['current_affiliation']}")
        
        # Run citation analysis
        dashboard_metrics = client.get_citation_metrics_for_dashboard()
        
        print(f"\n📊 Citation Metrics:")
        print(f"  • Total Citations: {dashboard_metrics['total_citations']}")
        print(f"  • Publications: {dashboard_metrics['publications_count']}")
        print(f"  • H-Index Approx: {dashboard_metrics['h_index_approximation']}")
        
        if dashboard_metrics.get('error'):
            print(f"  ⚠️  Error: {dashboard_metrics['error']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 ORCID Citation Analysis Tester")
    print("=" * 40)
    
    choice = input("Choose option:\n1. Test with default ORCID ID\n2. Test with custom ORCID ID\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_with_custom_orcid()
    else:
        test_citation_analysis() 