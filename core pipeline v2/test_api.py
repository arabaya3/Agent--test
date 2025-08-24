#!/usr/bin/env python3
"""
Test script for the Email Tools API Server
This script demonstrates how to use all the API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_home_endpoint():
    """Test the home endpoint with API documentation"""
    print("🏠 Testing Home Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
        print(f"Version: {data.get('version')}")
        print("Available endpoints:")
        for endpoint, info in data.get('endpoints', {}).items():
            print(f"  {info.get('method')} {endpoint}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_by_sender(sender="mena1006@menadevs.io"):
    """Test searching emails by sender"""
    print(f"📧 Testing Search by Sender: {sender}")
    try:
        response = requests.get(f"{BASE_URL}/api/emails/sender/{sender}")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"Success: {data.get('success')}")
            result = data.get('result', '')
            # Show first 200 characters of result
            print(f"Result preview: {result[:200]}...")
        else:
            print(f"Error: {data.get('error')}")
        
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_by_subject(subject="Test Email"):
    """Test searching emails by subject"""
    print(f"📝 Testing Search by Subject: {subject}")
    try:
        response = requests.get(f"{BASE_URL}/api/emails/subject/{subject}")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"Success: {data.get('success')}")
            result = data.get('result', '')
            # Show first 200 characters of result
            print(f"Result preview: {result[:200]}...")
        else:
            print(f"Error: {data.get('error')}")
        
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_by_id(email_id="AAMkAGExNmIwN2FiLTlkZTMtNDFkYS1iMzU0LTRhYjAxY2FmNTBmZQBGAAAAAAAG8Eghi479QL1MSPWXYND7BwBYKSXZRbf3QLZa1tvtP5EiAAAAAAEMAABYKSXZRbf3QLZa1tvtP5EiAAAKdkpKAAA="):
    """Test getting email details by ID"""
    print(f"🆔 Testing Search by Email ID: {email_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/emails/id/{email_id}")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"Success: {data.get('success')}")
            result = data.get('result', '')
            # Show first 200 characters of result
            print(f"Result preview: {result[:200]}...")
        else:
            print(f"Error: {data.get('error')}")
        
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_flexible_search():
    """Test the flexible search endpoint with POST requests"""
    print("🔍 Testing Flexible Search Endpoint...")
    
    test_cases = [
        {"search_type": "sender", "query": "mena1006@menadevs.io"},
        {"search_type": "subject", "query": "Test Email"},
        {"search_type": "id", "query": "AAMkAGExNmIwN2FiLTlkZTMtNDFkYS1iMzU0LTRhYjAxY2FmNTBmZQBGAAAAAAAG8Eghi479QL1MSPWXYND7BwBYKSXZRbf3QLZa1tvtP5EiAAAAAAEMAABYKSXZRbf3QLZa1tvtP5EiAAAKdkpKAAA="}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test case {i}: {test_case}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/emails/search",
                json=test_case,
                headers={'Content-Type': 'application/json'}
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                print(f"Success: {data.get('success')}")
                result = data.get('result', '')
                print(f"Result preview: {result[:200]}...")
            else:
                print(f"Error: {data.get('error')}")
            
            print("-" * 30)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 30)

def test_error_handling():
    """Test error handling with invalid requests"""
    print("❌ Testing Error Handling...")
    
    # Test with missing parameters
    try:
        response = requests.get(f"{BASE_URL}/api/emails/sender/")
        print(f"Empty sender - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with invalid search type
    try:
        response = requests.post(
            f"{BASE_URL}/api/emails/search",
            json={"search_type": "invalid", "query": "test"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Invalid search type - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test non-existent endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        print(f"Non-existent endpoint - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def main():
    """Run all tests"""
    print("🚀 Starting Email Tools API Tests")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Home Endpoint", test_home_endpoint),
        ("Search by Sender", lambda: test_search_by_sender()),
        ("Search by Subject", lambda: test_search_by_subject()),
        ("Search by ID", lambda: test_search_by_id()),
        ("Flexible Search", test_flexible_search),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
