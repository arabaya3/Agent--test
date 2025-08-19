#!/usr/bin/env python3
"""
Email Agent Setup for AIXPLAIN Platform
Integrates with existing Core Assistant Pipeline
"""

from aixplain.factories import AgentFactory, ModelFactory
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# AIXPLAIN Model IDs
GPT_4_ID = "669a63646eb56306647e1091"  # GPT-4 model ID
GPT_4O_MINI_ID = "669a63646eb56306647e1091"  # GPT-4o mini model ID

class EmailAgentSetup:
    def __init__(self):
        self.api_key = os.getenv('AIXPLAIN_API_KEY')
        self.team_api_key = os.getenv('TEAM_API_KEY')
        self.api_base_url = "http://localhost:8000"  # Your FastAPI server
        
        if not self.api_key:
            raise ValueError("AIXPLAIN_API_KEY not found in environment variables")
    
    def create_email_agent(self):
        """Create the Email Agent on AIXPLAIN platform"""
        print("🚀 Creating Email Agent on AIXPLAIN...")
        
        # Get the LLM instance and customize parameters
        try:
            llm = ModelFactory.get(GPT_4_ID)
            
            # Customize LLM parameters for email processing
            llm.model_params.temperature = 0.1
            llm.model_params.max_tokens = 2000
            llm.model_params.top_p = 0.9
            
            print("✓ LLM configured successfully")
            
        except Exception as e:
            print(f"⚠️ Using default LLM due to error: {e}")
            llm = None
        
        # Email Agent Instructions
        email_instructions = """
You are the Email Agent, specialized in email management and analysis using Microsoft Graph API with application permissions.

CORE RULES:
- ALWAYS use /users/{USER_ID}/... endpoints, NEVER use /me endpoints
- Parse relative dates (today, yesterday, last week) to YYYY-MM-DD format
- Always call tools to get data; never fabricate email information
- Return structured responses with count, summary, and items
- Handle natural language queries intelligently

CAPABILITIES:
- Retrieve emails by date range
- Find emails by sender and date
- Search emails by subject and date range
- Get specific emails by IDs
- Analyze email patterns and trends

DATE HANDLING:
- Convert "today" to current date
- Convert "yesterday" to previous day
- Convert "last week" to 7 days ago
- Convert "this week" to start of current week
- Convert "next week" to start of next week

RESPONSE FORMAT:
Always return JSON with:
- count: number of emails found
- summary: brief description of results
- items: array of email objects
- analysis: AI-powered insights about the emails

If no emails found, return count: 0 with appropriate summary.

EXAMPLES:
Query: "Show me emails from yesterday"
Action: Call email_by_date_range with yesterday's date
Response: {"count": 15, "summary": "Found 15 emails from yesterday", "items": [...], "analysis": "..."}

Query: "Find emails from john@company.com today"
Action: Call email_by_sender_date with sender and today's date
Response: {"count": 3, "summary": "Found 3 emails from john@company.com today", "items": [...], "analysis": "..."}
"""

        # Create the Email Agent
        try:
            email_agent = AgentFactory.create(
                name="Core Assistant Email Agent",
                description="Specialized agent for email management and analysis using Microsoft Graph API",
                instructions=email_instructions,
                llm=llm,
                api_key=self.api_key
            )
            
            print(f"✅ Email Agent created successfully!")
            print(f"📧 Agent ID: {email_agent.id}")
            print(f"🤖 Model: {email_agent.llm.model_params if email_agent.llm else 'Default'}")
            
            return email_agent
            
        except Exception as e:
            print(f"❌ Error creating Email Agent: {e}")
            return None
    
    def add_email_tools(self, agent_id):
        """Attach pre-created aiXplain tool assets to the Email Agent by ID.
        
        Note: Create HTTP/Web tools in the aiXplain UI, copy their asset IDs,
        and provide them via environment variables below.
        """
        print(f"\n🔧 Adding tools to Email Agent {agent_id}...")

        try:
            # Get the agent
            agent = AgentFactory.get(agent_id)

            # Read tool asset IDs from environment variables
            tool_env_to_name = [
                ("AIX_EMAIL_TOOL_DATE_RANGE_ID", "email_by_date_range"),
                ("AIX_EMAIL_TOOL_SENDER_DATE_ID", "email_by_sender_date"),
                ("AIX_EMAIL_TOOL_SUBJECT_RANGE_ID", "email_by_subject_date_range"),
                ("AIX_EMAIL_TOOL_BY_IDS_ID", "email_by_ids"),
            ]

            added_count = 0
            for env_key, friendly_name in tool_env_to_name:
                asset_id = os.getenv(env_key)
                if asset_id:
                    try:
                        tool = AgentFactory.create_model_tool(asset_id)
                        agent.tools.append(tool)
                        print(f"✓ Added tool '{friendly_name}' from asset ID {asset_id}")
                        added_count += 1
                    except Exception as tool_err:
                        print(f"⚠️ Failed to attach tool '{friendly_name}' ({asset_id}): {tool_err}")
                else:
                    print(f"ℹ️ Skipping '{friendly_name}': env var {env_key} not set")

            if added_count == 0:
                print("❌ No tool asset IDs provided. Set the env vars to attach tools:")
                print("   - AIX_EMAIL_TOOL_DATE_RANGE_ID")
                print("   - AIX_EMAIL_TOOL_SENDER_DATE_ID")
                print("   - AIX_EMAIL_TOOL_SUBJECT_RANGE_ID")
                print("   - AIX_EMAIL_TOOL_BY_IDS_ID")
                return False

            # Save the agent with new tools
            agent.save()

            print(f"✅ Added {added_count} tool(s) to Email Agent")
            return True

        except Exception as e:
            print(f"❌ Error adding tools: {e}")
            return False
    
    def test_email_agent(self, agent_id):
        """Test the Email Agent with sample queries"""
        print(f"\n🧪 Testing Email Agent {agent_id}...")
        
        try:
            # Get the agent
            agent = AgentFactory.get(agent_id)
            
            # Test queries
            test_queries = [
                "Show me emails from yesterday",
                "Find emails from john@company.com today",
                "Search for urgent emails from last week",
                "Get emails with subject containing 'project' from this week"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n🔍 Test {i}: {query}")
                print("-" * 50)
                
                try:
                    # Run the agent
                    response = agent.run(
                        query=query
                    )
                    
                    # Display results
                    print(f"✅ Success!")
                    print(f"📤 Output: {response.data['output']}")
                    print(f"🆔 Session ID: {response.data['session_id']}")
                    
                    # Show execution steps
                    if 'intermediate_steps' in response.data:
                        print(f"📊 Steps: {len(response.data['intermediate_steps'])} steps executed")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing agent: {e}")
            return False
    
    def deploy_email_agent(self, agent_id):
        """Deploy the Email Agent"""
        print(f"\n🚀 Deploying Email Agent {agent_id}...")
        
        try:
            # Get the agent
            agent = AgentFactory.get(agent_id)
            
            # Deploy the agent
            agent.deploy()
            
            print(f"✅ Email Agent deployed successfully!")
            print(f"🌐 API Endpoint: https://platform-api.aixplain.com/sdk/agents/{agent.id}/run")
            print(f"🔗 Dashboard: https://platform.aixplain.com/discover/agent/{agent.id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deploying agent: {e}")
            return False
    
    def setup_complete_email_agent(self):
        """Complete setup for Email Agent"""
        print("🎯 Setting up complete Email Agent on AIXPLAIN...")
        print("=" * 60)
        
        # Step 1: Create Agent
        print("\n1️⃣ Creating Email Agent...")
        email_agent = self.create_email_agent()
        
        if not email_agent:
            print("❌ Failed to create Email Agent. Exiting.")
            return None
        
        # Step 2: Add Tools
        print("\n2️⃣ Adding tools to Email Agent...")
        if not self.add_email_tools(email_agent.id):
            print("❌ Failed to add tools. Exiting.")
            return None
        
        # Step 3: Test Agent
        print("\n3️⃣ Testing Email Agent...")
        self.test_email_agent(email_agent.id)
        
        # Step 4: Deploy Agent
        print("\n4️⃣ Deploying Email Agent...")
        if not self.deploy_email_agent(email_agent.id):
            print("❌ Failed to deploy agent.")
            return None
        
        print(f"\n🎉 Email Agent setup complete!")
        print(f"📧 Agent ID: {email_agent.id}")
        print(f"🌐 API URL: https://platform-api.aixplain.com/sdk/agents/{email_agent.id}/run")
        print(f"🔗 Dashboard: https://platform.aixplain.com/discover/agent/{email_agent.id}")
        
        # Save agent info to file
        agent_info = {
            "agent_id": email_agent.id,
            "name": email_agent.name,
            "description": email_agent.description,
            "api_url": f"https://platform-api.aixplain.com/sdk/agents/{email_agent.id}/run",
            "dashboard_url": f"https://platform.aixplain.com/discover/agent/{email_agent.id}",
            "created_at": datetime.now().isoformat(),
            "tools": [tool.name for tool in email_agent.tools]
        }
        
        with open("email_agent_info.json", "w") as f:
            json.dump(agent_info, f, indent=2)
        
        print(f"💾 Agent information saved to email_agent_info.json")
        
        return email_agent

def main():
    """Main function to run the Email Agent setup"""
    try:
        setup = EmailAgentSetup()
        email_agent = setup.setup_complete_email_agent()
        
        if email_agent:
            print("\n✅ Email Agent setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start your FastAPI server: python api_server.py")
            print("2. Test the agent with real queries")
            print("3. Integrate with your main application")
        else:
            print("\n❌ Email Agent setup failed!")
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")

if __name__ == "__main__":
    main()
