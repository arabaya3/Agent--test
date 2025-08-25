#!/usr/bin/env python3

import requests
import json
import re
from typing import Dict, List, Optional, Tuple

class EmailAgent:
    
    def __init__(self, base_url: str = None):
        import os
        if base_url is None:
            base_url = os.getenv("PUBLIC_BASE_URL", "https://1b988f973611.ngrok-free.app")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def check_server_health(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def search_emails_by_sender(self, sender: str) -> Dict:
        try:
            response = self.session.get(f"{self.base_url}/api/emails/sender/{sender}")
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def search_emails_by_subject(self, subject: str) -> Dict:
        try:
            response = self.session.get(f"{self.base_url}/api/emails/subject/{subject}")
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_email_by_id(self, email_id: str) -> Dict:
        try:
            response = self.session.get(f"{self.base_url}/api/emails/id/{email_id}")
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def flexible_search(self, search_type: str, query: str) -> Dict:
        try:
            payload = {
                "search_type": search_type,
                "query": query
            }
            response = self.session.post(
                f"{self.base_url}/api/emails/search",
                json=payload
            )
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def parse_user_query(self, query: str) -> Tuple[str, str, str]:
        query_lower = query.lower()
        
        sender_patterns = [
            r"emails?\s+from\s+([^\s]+@[^\s]+)",
            r"find\s+emails?\s+from\s+([^\s]+@[^\s]+)",
            r"show\s+me\s+emails?\s+from\s+([^\s]+@[^\s]+)",
            r"messages?\s+from\s+([^\s]+@[^\s]+)"
        ]
        
        for pattern in sender_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return "search", "sender", match.group(1)
        
        subject_patterns = [
            r"emails?\s+about\s+([^\s]+)",
            r"emails?\s+with\s+subject\s+([^\s]+)",
            r"find\s+emails?\s+about\s+([^\s]+)",
            r"show\s+me\s+emails?\s+about\s+([^\s]+)"
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return "search", "subject", match.group(1)
        
        id_patterns = [
            r"email\s+id\s+([A-Za-z0-9+/=]+)",
            r"get\s+email\s+([A-Za-z0-9+/=]+)",
            r"details?\s+for\s+email\s+([A-Za-z0-9+/=]+)"
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return "get_details", "id", match.group(1)
        
        return "search", "subject", query.strip()
    
    def format_email_results(self, data: Dict, search_type: str) -> str:
        if "error" in data:
            return f"Error: {data['error']}"
        
        result_text = data.get("result", "")
        
        if not result_text:
            return f"No results found or API error occurred."
        
        lines = result_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith("Subject:") or line.startswith("From:") or line.startswith("Date:"):
                formatted_lines.append(f"• {line}")
            elif line.startswith("Email") and ":" in line:
                formatted_lines.append(f"• {line}")
        
        if formatted_lines:
            return "\n".join(formatted_lines)
        else:
            return result_text
    
    def answer_query(self, user_query: str) -> str:
        if not self.check_server_health():
            return "Email server is not available. Please make sure the Flask API server is running."
        
        action, search_type, query = self.parse_user_query(user_query)
        
        if not query:
            return "I couldn't understand your query. Please try rephrasing it."
        
        if action == "search":
            if search_type == "sender":
                result = self.search_emails_by_sender(query)
            elif search_type == "subject":
                result = self.search_emails_by_subject(query)
            else:
                result = self.flexible_search(search_type, query)
        elif action == "get_details":
            result = self.get_email_by_id(query)
        else:
            return "I couldn't determine what you're looking for. Please try rephrasing your query."
        
        return self.format_email_results(result, search_type)

def main():
    agent = EmailAgent()
    
    print("Email Agent Example")
    print("=" * 50)
    
    example_queries = [
        "Find emails from john@example.com",
        "Show me emails about meetings",
        "Get emails with subject project",
        "Find messages from sarah@company.com"
    ]
    
    for query in example_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        response = agent.answer_query(query)
        print(f"Response: {response}")
        print("-" * 30)

if __name__ == "__main__":
    main()
