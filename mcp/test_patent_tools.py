#!/usr/bin/env python3
"""
Test script for new MCP patent tools
Tests the three new endpoints: extract_patent_ids, generate_patent_urls, analyze_patent_text
"""

import json
import requests
import sys

# Test configuration
MCP_SERVER_URL = "http://localhost:8082"
API_KEY = "test-api-key"  # In production, use proper API key

def test_extract_patent_ids():
    """Test extract_patent_ids endpoint"""
    print("Testing extract_patent_ids endpoint...")
    
    payload = {
        "text": "I'm interested in US1234567, KR1020230001234, and WO2023056789A1 patents"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/extract_patent_ids",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: extract_patent_ids")
            print(f"   Found {len(result['data']['found'])} patents")
            for patent in result['data']['found']:
                print(f"   - {patent['id']} ({patent['country']})")
        else:
            print(f"❌ FAILED: extract_patent_ids - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: extract_patent_ids - {str(e)}")

def test_generate_patent_urls():
    """Test generate_patent_urls endpoint"""
    print("\nTesting generate_patent_urls endpoint...")
    
    payload = {
        "patent_ids": ["US1234567", "KR1020230001234", "WO2023056789A1"],
        "country": "auto",
        "sources": ["google"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/generate_patent_urls",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: generate_patent_urls")
            print(f"   Generated {len(result['data']['urls'])} URLs")
            for url in result['data']['urls']:
                print(f"   - {url['source']}: {url['url']}")
        else:
            print(f"❌ FAILED: generate_patent_urls - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: generate_patent_urls - {str(e)}")

def test_analyze_patent_text():
    """Test analyze_patent_text endpoint"""
    print("\nTesting analyze_patent_text endpoint...")
    
    payload = {
        "text": "I'm analyzing US1234567 and KR1020230001234 patents",
        "include_sources": ["google"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/analyze_patent_text",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: analyze_patent_text")
            print(f"   Analysis found {result['data']['summary']['patents_found']} patents")
            print(f"   Generated {result['data']['summary']['urls_generated']} URLs")
            
            # Show extracted patents
            for patent in result['data']['text_analysis']['found_patents']:
                print(f"   - {patent['id']} ({patent['country']})")
                
            # Show generated URLs
            for url in result['data']['url_generation']['urls']:
                print(f"   - {url['source']}: {url['url']}")
        else:
            print(f"❌ FAILED: analyze_patent_text - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: analyze_patent_text - {str(e)}")

def test_health_check():
    """Test MCP server health"""
    print("Testing MCP server health...")
    
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ SUCCESS: MCP server is healthy")
        else:
            print(f"❌ FAILED: Health check - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to MCP server - {str(e)}")
        print("   Make sure MCP server is running on port 8082")
        sys.exit(1)

def main():
    """Run all tests"""
    print("🧪 Testing MCP Patent Tools")
    print("=" * 50)
    
    # Test server health first
    test_health_check()
    
    # Test individual endpoints
    test_extract_patent_ids()
    test_generate_patent_urls() 
    test_analyze_patent_text()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()