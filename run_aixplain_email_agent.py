#!/usr/bin/env python3
"""
AIXPLAIN Email Agent Runner
Easy way to start and manage the AIXPLAIN Email Agent system
"""

import os
import sys
import subprocess
import time
import json
from dotenv import load_dotenv

load_dotenv()

def print_banner():
    """Print the application banner"""
    print("🎯 AIXPLAIN Email Agent System")
    print("=" * 50)
    print("Core Assistant Pipeline - Email Management")
    print("Powered by AIXPLAIN Platform")
    print("=" * 50)

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    required_vars = ['AIXPLAIN_API_KEY', 'CLIENT_ID', 'TENANT_ID', 'CLIENT_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("💡 Please update your .env file with the required variables")
        return False
    
    print("✅ Environment variables configured")
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting API Server...")
    
    try:
        # Check if server is already running
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is already running")
                return True
        except:
            pass
        
        # Start the server
        print("📡 Starting FastAPI server on http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        
        # Run the server in background
        process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server started successfully
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully")
                return True
            else:
                print(f"❌ API server returned status: {response.status_code}")
                return False
        except:
            print("❌ Failed to start API server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False

def setup_email_agent():
    """Set up the Email Agent on AIXPLAIN"""
    print("\n🤖 Setting up Email Agent on AIXPLAIN...")
    
    try:
        # Check if agent is already configured
        if os.path.exists("email_agent_info.json"):
            with open("email_agent_info.json", "r") as f:
                agent_info = json.load(f)
            
            print(f"✅ Email Agent already configured:")
            print(f"   📧 Agent ID: {agent_info.get('agent_id', 'N/A')}")
            print(f"   🌐 API URL: {agent_info.get('api_url', 'N/A')}")
            return True
        
        # Run the setup script
        print("🔧 Creating Email Agent...")
        result = subprocess.run([
            sys.executable, "email_agent_setup.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Email Agent setup completed")
            return True
        else:
            print(f"❌ Email Agent setup failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error setting up Email Agent: {e}")
        return False

def test_email_agent():
    """Test the Email Agent"""
    print("\n🧪 Testing Email Agent...")
    
    try:
        result = subprocess.run([
            sys.executable, "email_agent_client.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Email Agent test completed")
            return True
        else:
            print(f"❌ Email Agent test failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing Email Agent: {e}")
        return False

def run_interactive_mode():
    """Run interactive mode for testing queries"""
    print("\n💬 Interactive Mode")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 30)
    
    try:
        from email_agent_client import EmailAgentIntegration
        
        integration = EmailAgentIntegration()
        
        while True:
            try:
                query = input("\n🤖 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'help':
                    print("\n📋 Available commands:")
                    print("  - 'quit', 'exit', 'q': Exit interactive mode")
                    print("  - 'help': Show this help")
                    print("  - 'reset': Reset session")
                    print("  - Any natural language query about emails")
                    print("\n📝 Example queries:")
                    print("  - 'Show me emails from yesterday'")
                    print("  - 'Find emails from john@company.com today'")
                    print("  - 'Search for urgent emails from last week'")
                    print("  - 'Analyze my email patterns from this week'")
                    continue
                elif query.lower() == 'reset':
                    integration.reset_session()
                    continue
                elif not query:
                    continue
                
                # Process the query
                print("🔄 Processing...")
                result = integration.process_email_query(query)
                
                if result["success"]:
                    print(f"\n✅ Success!")
                    print(f"📊 Count: {result['count']}")
                    print(f"📝 Summary: {result['summary']}")
                    if result['analysis']:
                        print(f"🧠 Analysis: {result['analysis']}")
                else:
                    print(f"\n❌ Error: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    except ImportError:
        print("❌ Email Agent client not available")
        print("💡 Run the setup first: python email_agent_setup.py")

def show_menu():
    """Show the main menu"""
    print("\n📋 Available Options:")
    print("1. Test Environment")
    print("2. Start API Server")
    print("3. Setup Email Agent")
    print("4. Test Email Agent")
    print("5. Interactive Mode")
    print("6. Run All Tests")
    print("7. Exit")
    
    while True:
        try:
            choice = input("\n🎯 Choose an option (1-7): ").strip()
            
            if choice == '1':
                subprocess.run([sys.executable, "test_aixplain_setup.py"])
            elif choice == '2':
                start_api_server()
            elif choice == '3':
                setup_email_agent()
            elif choice == '4':
                test_email_agent()
            elif choice == '5':
                run_interactive_mode()
            elif choice == '6':
                print("\n🧪 Running all tests...")
                subprocess.run([sys.executable, "test_aixplain_setup.py"])
                print("\n🤖 Setting up Email Agent...")
                setup_email_agent()
                print("\n🧪 Testing Email Agent...")
                test_email_agent()
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not properly configured.")
        print("💡 Please check your .env file and try again.")
        return
    
    # Show menu
    show_menu()

if __name__ == "__main__":
    main()
