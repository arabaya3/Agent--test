#!/usr/bin/env python3
"""
Basic AIXPLAIN Test Script
Tests basic AIXPLAIN functionality without creating agents
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_aixplain_import():
    """Test basic AIXPLAIN import"""
    print("🔍 Testing AIXPLAIN import...")
    
    try:
        from aixplain.factories import AgentFactory, ModelFactory
        print("✅ AIXPLAIN factories imported successfully")
        return True
    except ImportError as e:
        print(f"❌ AIXPLAIN import failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    api_key = os.getenv('AIXPLAIN_API_KEY')
    if not api_key:
        print("❌ AIXPLAIN_API_KEY not found")
        return False
    
    print("✅ AIXPLAIN_API_KEY found")
    print(f"📝 API Key: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_model_factory():
    """Test ModelFactory functionality"""
    print("\n🔍 Testing ModelFactory...")
    
    try:
        from aixplain.factories import ModelFactory
        
        # Test getting a model
        model_id = "669a63646eb56306647e1091"  # GPT-4 model ID
        model = ModelFactory.get(model_id)
        
        print("✅ ModelFactory.get() works")
        print(f"📦 Model ID: {model.id}")
        return True
        
    except Exception as e:
        print(f"❌ ModelFactory test failed: {e}")
        return False

def test_agent_factory():
    """Test AgentFactory functionality"""
    print("\n🔍 Testing AgentFactory...")
    
    try:
        from aixplain.factories import AgentFactory
        
        # Test listing agents (this will test the connection)
        agents = AgentFactory.list()
        
        print("✅ AgentFactory.list() works")
        print(f"📊 Found {len(agents)} agents")
        return True
        
    except Exception as e:
        print(f"❌ AgentFactory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Basic AIXPLAIN Test")
    print("=" * 40)
    
    tests = [
        ("AIXPLAIN Import", test_aixplain_import),
        ("Environment Variables", test_environment),
        ("ModelFactory", test_model_factory),
        ("AgentFactory", test_agent_factory)
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
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AIXPLAIN is working correctly.")
        print("\n📋 Next steps:")
        print("1. Run: python email_agent_setup.py")
        print("2. Or run: python run_aixplain_email_agent.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Please check the errors above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
