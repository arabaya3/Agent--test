#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: {method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "result" in result:
                    # Truncate long results for display
                    result_text = result["result"]
                    if len(result_text) > 500:
                        result_text = result_text[:500] + "... (truncated)"
                    print(f"✅ SUCCESS: {result_text}")
                else:
                    print(f"✅ SUCCESS: {result}")
            except:
                print(f"✅ SUCCESS: {response.text[:200]}...")
        else:
            try:
                error = response.json()
                print(f"❌ ERROR: {error}")
            except:
                print(f"❌ ERROR: {response.text}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    print()

def main():
    print("Testing Core Pipeline API Endpoints")
    print("="*60)
    
    # Test health check first
    test_endpoint("/api/health", description="Health Check")
    
    # Test API documentation
    test_endpoint("/api/docs", description="API Documentation")
    
    # Test Email Tools
    test_endpoint("/api/emails/sender/test@example.com", description="Email by Sender")
    test_endpoint("/api/emails/subject/test", description="Email by Subject")
    
    # Test Calendar Tools
    test_endpoint("/api/calendar/date/2024-01-15", description="Calendar by Date")
    test_endpoint("/api/calendar/organizer/test@example.com/date/2024-01-15", description="Calendar by Organizer and Date")
    test_endpoint("/api/calendar/subject/meeting/start/2024-01-01/end/2024-01-31", description="Calendar by Subject and Date Range")
    
    # Test Meeting Tools
    test_endpoint("/api/meetings/title/test", description="Meeting by Title")
    
    # Test OneDrive Tools
    test_endpoint("/api/onedrive/files", description="OneDrive Files")
    test_endpoint("/api/onedrive/shared", description="OneDrive Shared Files")
    test_endpoint("/api/onedrive/file/file.txt", description="OneDrive File by Name")
    
    # Test POST endpoint
    test_endpoint("/api/emails/search", method="POST", 
                 data={"search_type": "sender", "query": "test@example.com"}, 
                 description="Email Search POST")
    
    print("\n" + "="*60)
    print("All endpoint tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
