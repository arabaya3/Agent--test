#!/usr/bin/env python3
"""
Enhanced Assistant Master - AIXPLAIN Smart Agent System
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import AIXPLAIN Smart Agent System
try:
    from agents import MasterAgent
    AGENT_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AIXPLAIN Agent System not available: {e}")
    AGENT_SYSTEM_AVAILABLE = False

# Import existing tools for fallback
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from calendar_tools.by_date_range import retrieve_meetings_by_date_range
from calendar_tools.by_date import retrieve_meetings_by_date
from calendar_tools.by_organizer_date import retrieve_meetings_by_organizer_date
from calendar_tools.by_subject_date_range import retrieve_meetings_by_subject_date_range
from meeting_tools.by_id import retrieve_meeting_by_id
from meeting_tools.by_title import retrieve_meetings_by_title
from meeting_tools.audience import retrieve_meeting_audience
from meeting_tools.attendance import retrieve_attendance_by_meeting_id
from meeting_tools.transcript import retrieve_transcript_by_meeting_id
from onedrive_tools.list_files import list_onedrive_files
from onedrive_tools.retrieve_files import retrieve_onedrive_file
from onedrive_tools.upload_files import upload_onedrive_file
from shared.auth import get_access_token
                            
load_dotenv()

class EnhancedAssistantMaster:
    """
    Enhanced Assistant Master with AIXPLAIN Smart Agent System
    """
    
    def __init__(self):
        self.user_id = os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        
        # Initialize AIXPLAIN Smart Agent System
        self.master_agent = None
        if AGENT_SYSTEM_AVAILABLE:
            try:
                self.master_agent = MasterAgent()
                print("✓ AIXPLAIN Smart Agent System initialized")
            except Exception as e:
                print(f"Warning: AIXPLAIN Agent System initialization failed: {e}")
                self.master_agent = None
        
        # Initialize authentication for fallback
        self.token = get_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else None
    
    def parse_relative_date(self, date_str: str) -> str:
        """Parse relative date strings to YYYY-MM-DD format"""
        today = datetime.now().date()
        date_str_lower = date_str.lower().strip()
        
        if date_str_lower == 'today':
            return today.strftime('%Y-%m-%d')
        elif date_str_lower == 'yesterday':
            return (today - timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str_lower == 'tomorrow':
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str_lower == 'last week':
            start_date = today - timedelta(days=today.weekday() + 7)
            return start_date.strftime('%Y-%m-%d')
        elif date_str_lower == 'this week':
            start_date = today - timedelta(days=today.weekday())
            return start_date.strftime('%Y-%m-%d')
        elif date_str_lower == 'next week':
            start_date = today + timedelta(days=7 - today.weekday())
            return start_date.strftime('%Y-%m-%d')
        else:
            # Try to parse as YYYY-MM-DD
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                raise ValueError("Dates must be in YYYY-MM-DD format or relative terms like 'today', 'yesterday', etc.")
    
    def process_query_with_agents(self, query: str) -> Dict[str, Any]:
        """
        Process query using AIXPLAIN Smart Agent System
        """
        if not self.master_agent:
            return {
                'error': 'AIXPLAIN Agent System not available',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Route query through master agent
            result = self.master_agent.route_query(query, self.user_id)
            return result
        except Exception as e:
            return {
                'error': f'Agent processing failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def process_query_fallback(self, query: str) -> Dict[str, Any]:
        """
        Fallback processing using rule-based logic
        """
        query_lower = query.lower().strip()
        
        # Email queries
        if any(word in query_lower for word in ['email', 'emails', 'mail', 'inbox']):
            return self._process_email_query(query)
        
        # Calendar/Meeting queries
        elif any(word in query_lower for word in ['meeting', 'meetings', 'calendar', 'schedule']):
            return self._process_meeting_query(query)
        
        # OneDrive/File queries
        elif any(word in query_lower for word in ['file', 'files', 'document', 'onedrive']):
            return self._process_file_query(query)
        
        # Chat queries
        elif any(word in query_lower for word in ['hello', 'hi', 'help', 'status']):
            return self._process_chat_query(query)
        
        else:
            return {
                'error': 'Query not recognized. Try asking about emails, meetings, files, or say hello.',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_email_query(self, query: str) -> Dict[str, Any]:
        """Process email-related queries"""
        query_lower = query.lower().strip()
        
        try:
            # Fetch recent email IDs
            fetch_last_email_ids(self.headers, limit=50, user_id=self.user_id)
            email_ids = get_cached_email_ids(limit=50)
            
            # Extract date information
            if 'today' in query_lower:
                date = datetime.now().strftime('%Y-%m-%d')
                emails = retrieve_emails_by_date_range(date, date, self.headers, email_ids, self.user_id)
            elif 'yesterday' in query_lower:
                date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                emails = retrieve_emails_by_date_range(date, date, self.headers, email_ids, self.user_id)
            elif 'this week' in query_lower:
                start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                emails = retrieve_emails_by_date_range(start_date, end_date, self.headers, email_ids, self.user_id)
            else:
                # Default to recent emails
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                emails = retrieve_emails_by_date_range(start_date, end_date, self.headers, email_ids, self.user_id)
            
            return {
                'type': 'email',
                'query': query,
                'items': emails,
                'count': len(emails),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Email processing failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_meeting_query(self, query: str) -> Dict[str, Any]:
        """Process meeting-related queries"""
        query_lower = query.lower().strip()
        
        try:
            # Extract date information
            if 'today' in query_lower:
                date = datetime.now().strftime('%Y-%m-%d')
                meetings = retrieve_meetings_by_date(date, self.user_id)
            elif 'yesterday' in query_lower:
                date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                meetings = retrieve_meetings_by_date(date, self.user_id)
            elif 'this week' in query_lower:
                start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                meetings = retrieve_meetings_by_date_range(start_date, end_date, self.user_id)
            else:
                # Default to recent meetings
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                meetings = retrieve_meetings_by_date_range(start_date, end_date, self.user_id)
            
            return {
                'type': 'meeting',
                'query': query,
                'items': meetings,
                'count': len(meetings),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Meeting processing failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_file_query(self, query: str) -> Dict[str, Any]:
        """Process file-related queries"""
        try:
            files = list_onedrive_files(user_id=self.user_id)
            
            return {
                'type': 'file',
                'query': query,
                'items': files,
                'count': len(files),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'File processing failed: {str(e)}',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_chat_query(self, query: str) -> Dict[str, Any]:
        """Process chat queries"""
        query_lower = query.lower().strip()
        
        if 'hello' in query_lower or 'hi' in query_lower:
            return {
                'type': 'chat',
                'query': query,
                'message': 'Hello! I\'m your AIXPLAIN-powered assistant. I can help you with emails, meetings, files, and more. What would you like to know?',
                'timestamp': datetime.now().isoformat()
            }
        elif 'help' in query_lower:
            return {
                'type': 'chat',
                'query': query,
                'message': 'I can help you with:\n- Emails: "Show me emails from today"\n- Meetings: "What meetings do I have this week?"\n- Files: "List my OneDrive files"\n- Status: "What\'s my status?"',
                'timestamp': datetime.now().isoformat()
            }
        elif 'status' in query_lower:
            agent_status = self.master_agent.get_agent_status() if self.master_agent else {'status': 'fallback_mode'}
            return {
                'type': 'chat',
                'query': query,
                'message': f'System Status: {json.dumps(agent_status, indent=2)}',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'type': 'chat',
                'query': query,
                'message': 'I\'m here to help! Try asking about emails, meetings, or files.',
                'timestamp': datetime.now().isoformat()
            }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main query processing method
        """
        print(f"🔍 Processing query: {query}")
        
        # Try AIXPLAIN Smart Agent System first
        if self.master_agent:
            try:
                result = self.process_query_with_agents(query)
                if 'error' not in result:
                    return result
            except Exception as e:
                print(f"Agent system failed, falling back: {e}")
        
        # Fallback to rule-based processing
        return self.process_query_fallback(query)

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    AIXPLAIN SMART AGENT SYSTEM               ║
║                    Core Assistant Pipeline                   ║
║                                                              ║
║  🧠 Master Agent + Specialized Agents                       ║
║  📧 Email Agent    📅 Calendar Agent                        ║
║  📁 OneDrive Agent 🎯 Meeting Agent                         ║
║                                                              ║
║  Powered by AIXPLAIN SDK v0.2.33                            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def interactive_mode():
    """Interactive mode for user queries"""
    assistant = EnhancedAssistantMaster()
    
    print_banner()
    print("🎯 Interactive Mode - AIXPLAIN Smart Agent System")
    print("Type 'quit' or 'exit' to leave")
    print("Type 'help' for available commands")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n🤖 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thanks for using the AIXPLAIN Smart Agent System.")
                break
            
            if not query:
                continue
            
            # Process query
            result = assistant.process_query(query)
            
            # Display results
            print(f"\n📊 Result:")
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            elif 'message' in result:
                print(f"💬 {result['message']}")
            else:
                count = result.get('count', 0)
                print(f"✅ {result.get('summary', f'Found {count} items')}")
                
                # Show AIXPLAIN analysis if available
                if 'aixplain_analysis' in result and result['aixplain_analysis']:
                    print(f"\n🧠 AIXPLAIN Analysis:")
                    analysis = result['aixplain_analysis']
                    if 'summary' in analysis:
                        print(f"📝 {analysis['summary']}")
                
                # Show items (limited to first 3)
                items = result.get('items', [])
                if items:
                    print(f"\n📋 Items (showing first 3 of {len(items)}):")
                    for i, item in enumerate(items[:3]):
                        if isinstance(item, dict):
                            if 'subject' in item:
                                print(f"  {i+1}. {item['subject']}")
                            elif 'name' in item:
                                print(f"  {i+1}. {item['name']}")
                            else:
                                print(f"  {i+1}. {str(item)[:100]}...")
                        else:
                            print(f"  {i+1}. {str(item)[:100]}...")
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the AIXPLAIN Smart Agent System.")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Please try again or type 'help' for assistance.")

def batch_mode(queries: List[str]):
    """Batch mode for processing multiple queries"""
    assistant = EnhancedAssistantMaster()
    
    print_banner()
    print("📦 Batch Mode - AIXPLAIN Smart Agent System")
    print(f"Processing {len(queries)} queries...")
    print("=" * 60)
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Processing query {i}/{len(queries)}: {query}")
        
        try:
            result = assistant.process_query(query)
            results.append(result)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                count = result.get('count', 0)
                print(f"✅ Success: {result.get('summary', f'Found {count} items')}")
            
        except Exception as e:
            error_result = {'error': str(e), 'query': query, 'timestamp': datetime.now().isoformat()}
            results.append(error_result)
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Batch Processing Complete")
    print(f"✅ Successful: {len([r for r in results if 'error' not in r])}")
    print(f"❌ Failed: {len([r for r in results if 'error' in r])}")
    
    return results

def demo_mode():
    """Demo mode with sample queries"""
    demo_queries = [
        "hello",
        "emails from today",
        "meetings this week",
        "list my OneDrive files",
        "help"
    ]
    
    print_banner()
    print("🎬 Demo Mode - AIXPLAIN Smart Agent System")
    print("Running sample queries to demonstrate capabilities...")
    print("=" * 60)
    
    return batch_mode(demo_queries)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'batch' and len(sys.argv) > 2:
            # Batch mode with queries from command line
            queries = sys.argv[2:]
            batch_mode(queries)
        elif command == 'demo':
            # Demo mode
            demo_mode()
        elif command == 'help':
            # Help
            print_banner()
            print("""
Usage:
  python enhanced_assistant_master.py                    # Interactive mode
  python enhanced_assistant_master.py batch <queries>   # Batch mode
  python enhanced_assistant_master.py demo              # Demo mode
  python enhanced_assistant_master.py help              # This help

Examples:
  python enhanced_assistant_master.py batch "emails from today" "meetings this week"
  python enhanced_assistant_master.py demo
            """)
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for usage information.")
    else:
        # Interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()
