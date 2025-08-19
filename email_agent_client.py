#!/usr/bin/env python3
"""
Email Agent Client for AIXPLAIN Integration
Integrates with the main Core Assistant Pipeline
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

class EmailAgentClient:
    """
    Client for interacting with AIXPLAIN Email Agent
    """
    
    def __init__(self, agent_id: Optional[str] = None, api_key: Optional[str] = None):
        self.agent_id = agent_id or os.getenv('AIXPLAIN_EMAIL_AGENT_ID')
        self.api_key = api_key or os.getenv('AIXPLAIN_API_KEY')
        self.base_url = "https://platform-api.aixplain.com/sdk/agents"
        
        if not self.agent_id:
            raise ValueError("Email Agent ID not found. Set AIXPLAIN_EMAIL_AGENT_ID in environment or pass agent_id parameter.")
        
        if not self.api_key:
            raise ValueError("AIXPLAIN API Key not found. Set AIXPLAIN_API_KEY in environment or pass api_key parameter.")
    
    def query_emails(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Query the Email Agent with a natural language query
        
        Args:
            query: Natural language query about emails
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dictionary with response data
        """
        url = f"{self.base_url}/{self.agent_id}/run"
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "query": query
        }
        
        if session_id:
            data["sessionId"] = session_id
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "output": result.get("output"),
                "session_id": result.get("session_id"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "execution_stats": result.get("execution_stats", {}),
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "output": None,
                "session_id": None,
                "intermediate_steps": [],
                "execution_stats": {}
            }
    
    def get_result(self, request_id: str) -> Dict[str, Any]:
        """
        Get result by request ID for long-running operations
        
        Args:
            request_id: The request ID from a previous query
            
        Returns:
            Dictionary with result data
        """
        url = f"{self.base_url}/{request_id}/result"
        
        headers = {
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the Email Agent
        
        Returns:
            Dictionary with agent information
        """
        url = f"{self.base_url}/{self.agent_id}"
        
        headers = {
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def test_connection(self) -> bool:
        """
        Test connection to the Email Agent
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            info = self.get_agent_info()
            return "error" not in info
        except Exception:
            return False

class EmailAgentIntegration:
    """
    Integration class for using Email Agent with Core Assistant Pipeline
    """
    
    def __init__(self):
        self.client = EmailAgentClient()
        self.session_id = None
    
    def process_email_query(self, query: str) -> Dict[str, Any]:
        """
        Process an email-related query using the AIXPLAIN Email Agent
        
        Args:
            query: Natural language query about emails
            
        Returns:
            Dictionary with processed results
        """
        print(f"🤖 Processing email query with AIXPLAIN: {query}")
        
        # Query the Email Agent
        result = self.client.query_emails(query, self.session_id)
        
        if result["success"]:
            # Update session ID for conversation continuity
            self.session_id = result["session_id"]
            
            # Parse the output
            try:
                if isinstance(result["output"], str):
                    # Try to parse JSON output
                    parsed_output = json.loads(result["output"])
                else:
                    parsed_output = result["output"]
                
                return {
                    "success": True,
                    "agent_used": "AIXPLAIN Email Agent",
                    "count": parsed_output.get("count", 0),
                    "summary": parsed_output.get("summary", ""),
                    "items": parsed_output.get("items", []),
                    "analysis": parsed_output.get("analysis", ""),
                    "session_id": self.session_id,
                    "intermediate_steps": result["intermediate_steps"]
                }
                
            except (json.JSONDecodeError, TypeError) as e:
                # If output is not JSON, return as is
                return {
                    "success": True,
                    "agent_used": "AIXPLAIN Email Agent",
                    "count": 0,
                    "summary": "AIXPLAIN Email Agent processed the query",
                    "items": [],
                    "analysis": result["output"],
                    "session_id": self.session_id,
                    "intermediate_steps": result["intermediate_steps"]
                }
        else:
            return {
                "success": False,
                "error": result["error"],
                "agent_used": "AIXPLAIN Email Agent (Failed)",
                "count": 0,
                "summary": "Failed to process query with AIXPLAIN Email Agent",
                "items": [],
                "analysis": ""
            }
    
    def get_emails_by_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get emails within a date range using AIXPLAIN Email Agent
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with email results
        """
        query = f"Show me emails from {start_date} to {end_date}"
        return self.process_email_query(query)
    
    def get_emails_by_sender(self, sender: str, date: str) -> Dict[str, Any]:
        """
        Get emails from a specific sender on a specific date
        
        Args:
            sender: Email address of sender
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with email results
        """
        query = f"Find emails from {sender} on {date}"
        return self.process_email_query(query)
    
    def search_emails_by_subject(self, subject: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Search emails by subject keyword within date range
        
        Args:
            subject: Subject keyword to search for
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with email results
        """
        query = f"Search for emails with subject containing '{subject}' from {start_date} to {end_date}"
        return self.process_email_query(query)
    
    def get_emails_by_ids(self, email_ids: List[str]) -> Dict[str, Any]:
        """
        Get specific emails by their IDs
        
        Args:
            email_ids: List of email IDs
            
        Returns:
            Dictionary with email results
        """
        query = f"Get emails with IDs: {', '.join(email_ids)}"
        return self.process_email_query(query)
    
    def analyze_email_patterns(self, date_range: str = "last week") -> Dict[str, Any]:
        """
        Analyze email patterns using AIXPLAIN Email Agent
        
        Args:
            date_range: Date range for analysis (e.g., "last week", "this month")
            
        Returns:
            Dictionary with analysis results
        """
        query = f"Analyze my email patterns from {date_range}"
        return self.process_email_query(query)
    
    def reset_session(self):
        """Reset the conversation session"""
        self.session_id = None
        print("🔄 Email Agent session reset")

def test_email_agent_integration():
    """Test the Email Agent integration"""
    print("🧪 Testing Email Agent Integration...")
    
    try:
        integration = EmailAgentIntegration()
        
        # Test connection
        if not integration.client.test_connection():
            print("❌ Failed to connect to Email Agent")
            return False
        
        print("✅ Connected to Email Agent successfully")
        
        # Test queries
        test_queries = [
            "Show me emails from yesterday",
            "Find emails from john@company.com today",
            "Search for urgent emails from last week",
            "Analyze my email patterns from this week"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 50)
            
            result = integration.process_email_query(query)
            
            if result["success"]:
                print(f"✅ Success!")
                print(f"📊 Count: {result['count']}")
                print(f"📝 Summary: {result['summary']}")
                if result['analysis']:
                    print(f"🧠 Analysis: {result['analysis']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the integration
    test_email_agent_integration()
