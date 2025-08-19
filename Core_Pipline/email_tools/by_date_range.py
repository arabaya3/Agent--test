import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
import time
try:
    from .shared_email_ids import fetch_last_email_ids, get_cached_email_ids
except ImportError:
    # Allow running this file directly: python email_tools/by_date_range.py
    import sys, os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from shared.auth import get_access_token

load_dotenv()

def get_conversation_messages(conversation_id, headers, user_id=None):
    from urllib.parse import quote
    import time
    base_url = "https://graph.microsoft.com/v1.0"
    
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if target_user:
        user_prefix = f"users/{target_user}"
    else:
        user_prefix = "me"
    
    search_url = f"{base_url}/{user_prefix}/messages?$search=\"conversationId:{conversation_id}\"&$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,body,bodyPreview"
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                return messages
    except requests.exceptions.RequestException:
        pass
    
    allitems_url = (
        f"{base_url}/{user_prefix}/mailFolders/msgfolderroot/messages?"
        f"$filter=conversationId eq '{conversation_id}'&$orderby=sentDateTime asc&$top=50&$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,body,bodyPreview"
    )
    try:
        response = requests.get(allitems_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                return messages
    except requests.exceptions.RequestException:
        pass
    
    inbox_url = (
        f"{base_url}/{user_prefix}/mailFolders/inbox/messages?"
        f"$filter=conversationId eq '{conversation_id}'&$orderby=sentDateTime asc&$top=50&$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,body,bodyPreview"
    )
    try:
        response = requests.get(inbox_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                return messages
    except requests.exceptions.RequestException:
        pass
    
    all_msgs = []
    next_url = f"{base_url}/{user_prefix}/messages?$top=100&$orderby=receivedDateTime desc&$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,body,bodyPreview"
    message_count = 0
    max_messages = 100                              
    
    while next_url and message_count < max_messages:
        try:
            response = requests.get(next_url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                batch = data.get("value", [])
                filtered = [m for m in batch if m.get("conversationId") == conversation_id]
                all_msgs.extend(filtered)
                message_count += len(batch)
                next_url = data.get("@odata.nextLink")
                if next_url:
                    time.sleep(0.1)                 
            else:
                break
        except requests.exceptions.RequestException:
            break
    
    if all_msgs:
        all_msgs.sort(key=lambda m: m.get("sentDateTime", ""))
        return all_msgs
    
    return []

def search_emails_by_date_range(start_date, end_date, headers, email_ids, user_id=None):
    # Backward-compat wrapper: keep signature but do a direct Graph query by date range
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return []

    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set and no user_id provided.")
        return []

    base_url = "https://graph.microsoft.com/v1.0"
    url = (
        f"{base_url}/users/{target_user}/messages?"
        f"$filter=receivedDateTime ge {start_datetime} and receivedDateTime le {end_datetime}"
        f"&$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,bodyPreview"
        f"&$orderby=receivedDateTime desc&$top=50"
    )

    results = []
    while url:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                print(f"Error querying messages: HTTP {resp.status_code}\n{resp.text}")
                break
            data = resp.json()
            batch = data.get("value", [])
            results.extend(batch)
            url = data.get("@odata.nextLink")
            # Guardrail to avoid excessive downloads
            if len(results) >= 1000:
                break
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            break

    return results

def retrieve_emails_by_date_range(start_date, end_date, headers, email_ids, user_id=None):
    emails = search_emails_by_date_range(start_date, end_date, headers, email_ids, user_id)
    
    if not emails:
        print("No emails found in the specified date range.")
        return []
    
    all_conversation_emails = []
    processed_conversation_ids = set()
    
    for email in emails:
        conversation_id = email.get("conversationId")
        if not conversation_id:
            continue
            
        if conversation_id in processed_conversation_ids:
            continue
        processed_conversation_ids.add(conversation_id)
        
        conversation_messages = get_conversation_messages(conversation_id, headers, user_id)
        if not conversation_messages:
            continue
            
        msg_dict = {}
        
        orig_id = str(email.get("id")).lower()
        msg_dict[orig_id] = {
            "id": email.get("id"),
            "subject": email.get("subject", "No Subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email.get("receivedDateTime"),
            "hasAttachments": email.get("hasAttachments", False),
            "bodyPreview": (email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"),
            "body": (email.get("body", {}) or {}).get("content", ""),
            "conversationId": email.get("conversationId")
        }
        
        for msg in conversation_messages:
            msg_id = str(msg.get("id")).lower()
            msg_dict[msg_id] = {
                "id": msg.get("id"),
                "subject": msg.get("subject", "No Subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "receivedDateTime": msg.get("receivedDateTime"),
                "hasAttachments": msg.get("hasAttachments", False),
                "bodyPreview": (msg.get("bodyPreview", "")[:100] + "..." if msg.get("bodyPreview") else "No preview"),
                "body": (msg.get("body", {}) or {}).get("content", ""),
                "conversationId": msg.get("conversationId")
            }
        
        output_msgs = sorted(msg_dict.values(), key=lambda m: m.get("receivedDateTime", ""))
        all_conversation_emails.extend(output_msgs)
    
def retrieve_emails_by_date_range(start_date, end_date, headers, email_ids, user_id=None, max_emails=None):
    emails = search_emails_by_date_range(start_date, end_date, headers, email_ids, user_id)
    
    if not emails:
        print("No emails found in the specified date range.")
        return []
    
    all_conversation_emails = []
    processed_conversation_ids = set()
    
    for email in emails:
        conversation_id = email.get("conversationId")
        if not conversation_id:
            continue
            
        if conversation_id in processed_conversation_ids:
            continue
        processed_conversation_ids.add(conversation_id)
        
        conversation_messages = get_conversation_messages(conversation_id, headers, user_id)
        if not conversation_messages:
            continue
            
        msg_dict = {}
        
        orig_id = str(email.get("id")).lower()
        msg_dict[orig_id] = {
            "id": email.get("id"),
            "subject": email.get("subject", "No Subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email.get("receivedDateTime"),
            "hasAttachments": email.get("hasAttachments", False),
            "bodyPreview": (email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"),
            "body": (email.get("body", {}) or {}).get("content", ""),
            "conversationId": email.get("conversationId")
        }
        
        for msg in conversation_messages:
            msg_id = str(msg.get("id")).lower()
            msg_dict[msg_id] = {
                "id": msg.get("id"),
                "subject": msg.get("subject", "No Subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "receivedDateTime": msg.get("receivedDateTime"),
                "hasAttachments": msg.get("hasAttachments", False),
                "bodyPreview": (msg.get("bodyPreview", "")[:100] + "..." if msg.get("bodyPreview") else "No preview"),
                "body": (msg.get("body", {}) or {}).get("content", ""),
                "conversationId": msg.get("conversationId")
            }
        
        output_msgs = sorted(msg_dict.values(), key=lambda m: m.get("receivedDateTime", ""))
        all_conversation_emails.extend(output_msgs)
    
    # Limit the results to max_emails if specified
    if max_emails and len(all_conversation_emails) > max_emails:
        all_conversation_emails = sorted(all_conversation_emails, key=lambda m: m.get("receivedDateTime", ""), reverse=True)[:max_emails]
        all_conversation_emails = sorted(all_conversation_emails, key=lambda m: m.get("receivedDateTime", ""))
    
    if all_conversation_emails:
        print("\n" + "=" * 80)
        print("📧 EMAIL MESSAGES RETRIEVED")
        print("=" * 80)
        
        for i, email in enumerate(all_conversation_emails, 1):
            print(f"\n📨 EMAIL #{i}")
            print("─" * 60)
            
            # Header section
            print(f"📋 SUBJECT: {email['subject']}")
            print(f"👤 FROM: {email['from']}")
            print(f"📅 DATE: {email['receivedDateTime']}")
            print(f"📎 ATTACHMENTS: {'Yes' if email['hasAttachments'] else 'No'}")
            
            # Body section
            print(f"\n📝 BODY CONTENT:")
            print("─" * 40)
            
            body_content = email.get('body', '')
            if body_content:
                # Clean up HTML tags and format the body
                import re
                # Remove HTML tags
                clean_body = re.sub(r'<[^>]+>', '', body_content)
                # Remove HTML entities
                clean_body = re.sub(r'&nbsp;', ' ', clean_body)
                clean_body = re.sub(r'&amp;', '&', clean_body)
                clean_body = re.sub(r'&lt;', '<', clean_body)
                clean_body = re.sub(r'&gt;', '>', clean_body)
                clean_body = re.sub(r'&quot;', '"', clean_body)
                # Remove extra whitespace but preserve line breaks
                clean_body = re.sub(r'[ \t]+', ' ', clean_body)
                clean_body = re.sub(r'\n\s*\n', '\n\n', clean_body)
                clean_body = clean_body.strip()
                
                if clean_body:
                    # Format the body with proper line breaks
                    lines = clean_body.split('\n')
                    formatted_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Wrap long lines for better readability
                            if len(line) > 100:
                                words = line.split()
                                current_line = ""
                                for word in words:
                                    if len(current_line + word) > 100:
                                        if current_line:
                                            formatted_lines.append(current_line.strip())
                                        current_line = word
                                    else:
                                        current_line += " " + word if current_line else word
                                if current_line:
                                    formatted_lines.append(current_line.strip())
                            else:
                                formatted_lines.append(line)
                    
                    # Print formatted body
                    for line in formatted_lines:
                        print(f"{line}")
                else:
                    print("No readable body content available")
            else:
                print("No body content available")
            
            print("─" * 60)
            print("")  # Add spacing between emails
    
    return all_conversation_emails

def main():
    print("============================================================")
    print("Email Date Range Retriever")
    print("============================================================")
    
                             
    access_token = get_access_token()
    if not access_token:
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
                                                  
    try:
        limit = int(input("How many recent emails do you want to fetch? (1-100, default 100): ").strip() or 100)
    except ValueError:
        limit = 100
    limit = min(max(1, limit), 100)
                                          
    fetch_last_email_ids(headers, limit=limit)
    email_ids = get_cached_email_ids(limit=limit)
    
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if not start_date:
        print("Error: Start date is required")
        return
    
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    if not end_date:
        print("Error: End date is required")
        return
    
    emails = retrieve_emails_by_date_range(start_date, end_date, headers, email_ids, max_emails=limit)

if __name__ == "__main__":
    main() 