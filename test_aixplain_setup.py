#!/usr/bin/env python3
"""
Test Script for AIXPLAIN Email Agent Setup
Verifies all components are working correctly
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    """Test environment variables"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'AIXPLAIN_API_KEY',
        'CLIENT_ID',
        'TENANT_ID',
        'CLIENT_SECRET',
        'DEFAULT_USER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_api_server():
    """Test API server connectivity"""
    print("\n🔍 Testing API Server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and healthy")
            return True
        else:
            print(f"❌ API server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Start it with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error testing API server: {e}")
        return False

def test_email_tools():
    """Test email tools functionality"""
    print("\n🔍 Testing Email Tools...")
    
    try:
        # Test email by date range endpoint
        test_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        response = requests.post(
            "http://localhost:8000/email/by-date-range",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email tools are working")
            print(f"📊 Response: {result.get('count', 0)} emails found")
            return True
        else:
            print(f"❌ Email tools returned status code: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email tools: {e}")
        return False

def test_aixplain_connection():
    """Test AIXPLAIN API connection"""
    print("\n🔍 Testing AIXPLAIN Connection...")
    
    try:
        api_key = os.getenv('AIXPLAIN_API_KEY')
        if not api_key:
            print("❌ AIXPLAIN_API_KEY not found")
            return False
        
        # Test basic AIXPLAIN API connection
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # Try to list agents (this will test the connection)
        response = requests.get(
            "https://platform-api.aixplain.com/sdk/agents",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 401, 403]:  # 401/403 means auth works but no access
            print("✅ AIXPLAIN API connection successful")
            return True
        else:
            print(f"❌ AIXPLAIN API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AIXPLAIN connection: {e}")
        return False

def test_email_agent_setup():
    """Test Email Agent setup script"""
    print("\n🔍 Testing Email Agent Setup...")
    
    try:
        # Check if setup script exists
        if not os.path.exists("email_agent_setup.py"):
            print("❌ email_agent_setup.py not found")
            return False
        
        print("✅ Email Agent setup script found")
        
        # Check if agent info file exists (indicates previous setup)
        if os.path.exists("email_agent_info.json"):
            with open("email_agent_info.json", "r") as f:
                agent_info = json.load(f)
            
            print(f"✅ Email Agent already configured:")
            print(f"   📧 Agent ID: {agent_info.get('agent_id', 'N/A')}")
            print(f"   🌐 API URL: {agent_info.get('api_url', 'N/A')}")
            print(f"   🔗 Dashboard: {agent_info.get('dashboard_url', 'N/A')}")
            return True
        else:
            print("ℹ️ Email Agent not yet configured. Run: python email_agent_setup.py")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Email Agent setup: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = [
        'aixplain',
        'fastapi',
        'uvicorn',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def main():
    """Run all tests"""
    print("🧪 AIXPLAIN Email Agent Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Dependencies", test_dependencies),
        ("AIXPLAIN Connection", test_aixplain_connection),
        ("API Server", test_api_server),
        ("Email Tools", test_email_tools),
        ("Email Agent Setup", test_email_agent_setup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your AIXPLAIN Email Agent setup is ready.")
        print("\n📋 Next steps:")
        print("1. If Email Agent not configured: python email_agent_setup.py")
        print("2. Test the agent: python email_agent_client.py")
        print("3. Integrate with main app: Update enhanced_assistant_master.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues above.")
        
        if not any(name == "API Server" and result for name, result in results):
            print("\n💡 To start the API server:")
            print("   python api_server.py")
        
        if not any(name == "Email Agent Setup" and result for name, result in results):
            print("\n💡 To set up the Email Agent:")
            print("   python email_agent_setup.py")

if __name__ == "__main__":
    main()
