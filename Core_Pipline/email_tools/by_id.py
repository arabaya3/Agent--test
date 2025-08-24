import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
import time
try:
    from .shared_email_ids import fetch_last_email_ids, get_cached_email_ids, get_access_token
except ImportError:
    import sys, os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids, get_access_token

load_dotenv()

def get_email_by_id(email_id, headers, user_id=None):
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return None
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/messages/{email_id}?$select=id,subject,from,receivedDateTime,hasAttachments,conversationId,body,bodyPreview"
    try:
    
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Error: Email with ID '{email_id}' not found (404)")
            print(f"Possible reasons: Email was deleted, ID is invalid, or email is in a different mailbox")
            return None
        elif response.status_code == 400:
            print(f"Error: Bad request for email ID '{email_id}' (400)")
            print(f"Response: {response.text}")
            print(f"Possible reasons: Invalid email ID format, ID contains special characters, or ID is malformed")
            return None
        elif response.status_code == 403:
            print(f"Error: Access denied for email ID '{email_id}' (403)")
            print(f"Possible reasons: Insufficient permissions or email is in a different mailbox")
            return None
        else:
            print(f"Error retrieving email {email_id}: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print(f"Error: Timeout while retrieving email {email_id}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving email {email_id}: {e}")
        return None

def get_conversation_messages(conversation_id, headers, user_id=None):
    from urllib.parse import quote
    import time
    base_url = "https://graph.microsoft.com/v1.0"
    
                                                               
    if user_id:
        user_prefix = f"users/{user_id}"
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

def get_recent_email_ids(headers, limit=10, user_id=None):
    if user_id:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages?$top={limit}&$select=id,subject,from,receivedDateTime&$orderby=receivedDateTime desc"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}&$select=id,subject,from,receivedDateTime&$orderby=receivedDateTime desc"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            emails = response.json().get("value", [])
            print(f"\nRecent {len(emails)} emails (use these IDs for testing):")
            print("=" * 80)
            for i, email in enumerate(emails, 1):
                subject = email.get("subject", "No Subject")
                sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                date = email.get("receivedDateTime", "Unknown")
                email_id = email.get("id", "No ID")
                print(f"{i}. ID: {email_id}")
                print(f"   Subject: {subject}")
                print(f"   From: {sender}")
                print(f"   Date: {date}")
                print()
            return [email.get("id") for email in emails]
        else:
            print(f"Error getting recent emails: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error getting recent emails: {e}")
        return []

def search_emails_by_id(headers, email_ids):
    emails = []
    for eid in email_ids:
        url = f"https://graph.microsoft.com/v1.0/me/messages/{eid}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                emails.append(response.json())
        except Exception:
            continue
    
    return emails

def retrieve_emails_by_ids(email_ids, headers, user_id=None):
    print("============================================================")
    print("Email ID Retriever (with Conversation Thread)")
    print("============================================================")
                                                                       
    all_conversation_emails = []
    processed_conversation_ids = set()                                                     
    unique_conversations_processed = 0                                                 
    for i, email_id in enumerate(email_ids, 1):
        email_data = get_email_by_id(email_id, headers, user_id)
        if not email_data:
            continue
        conversation_id = email_data.get("conversationId")
        if not conversation_id:
            continue
            
                                                            
        if conversation_id in processed_conversation_ids:
            continue
        processed_conversation_ids.add(conversation_id)
        unique_conversations_processed += 1
        
        conversation_messages = get_conversation_messages(conversation_id, headers, user_id)
        if not conversation_messages:
            continue
            
                                                                                                  
        msg_dict = {}
        
                                      
        orig_id = str(email_data.get("id")).lower()
        msg_dict[orig_id] = {
            "id": email_data.get("id"),
            "subject": email_data.get("subject", "No Subject"),
            "from": email_data.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email_data.get("receivedDateTime"),
            "hasAttachments": email_data.get("hasAttachments", False),
            "bodyPreview": (email_data.get("bodyPreview", "")[:100] + "..." if email_data.get("bodyPreview") else "No preview"),
            "body": (email_data.get("body", {}) or {}).get("content", ""),
            "conversationId": email_data.get("conversationId")
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
    print("Email By ID Retriever")
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
    emails_info = []
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot fetch emails.")
        return
        
    for eid in email_ids:
        url = f"https://graph.microsoft.com/v1.0/users/{target_user}/messages/{eid}?$select=id,subject"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                emails_info.append({"id": data.get("id"), "subject": data.get("subject", "No Subject")})
        except Exception:
            continue
    if not emails_info:
        print("No recent emails found.")
        return
    print("\nRecent Emails:")
    print("============================================================")
    for idx, info in enumerate(emails_info, 1):
        print(f"{idx}. ID: {info['id']}")
        print(f"   Subject: {info['subject']}")
    print("============================================================")
    print("Enter the numbers of the emails you want to retrieve (comma-separated, e.g., 1,3,5): ", end="")
    selected = input().strip()
    if not selected:
        print("No selection made.")
        return
    try:
        selected_indices = [int(x.strip()) for x in selected.split(",") if x.strip().isdigit()]
    except Exception:
        print("Invalid input.")
        return
    selected_ids = [emails_info[i-1]["id"] for i in selected_indices if 1 <= i <= len(emails_info)]
    if not selected_ids:
        print("No valid email numbers selected.")
        return
    emails = retrieve_emails_by_ids(selected_ids, headers, target_user)                                 
    if not emails:
        print("\nNo emails were retrieved. Would you like to see recent email IDs to try again? (y/n): ", end="")
        retry = input().strip().lower()
        if retry == 'y':
            get_recent_email_ids(headers, 10, target_user)
    
    # Ask if user wants to select more emails
    while True:
        print("\n" + "=" * 60)
        print("📧 EMAIL SELECTION MENU")
        print("=" * 60)
        print("1. Select another email from the list")
        print("2. Show recent emails list again")
        print("3. Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            # Show the email list again
            print("\nRecent Emails:")
            print("=" * 60)
            for idx, info in enumerate(emails_info, 1):
                print(f"{idx}. ID: {info['id']}")
                print(f"   Subject: {info['subject']}")
            print("=" * 60)
            
            print("Enter the numbers of the emails you want to retrieve (comma-separated, e.g., 1,3,5): ", end="")
            selected = input().strip()
            if not selected:
                print("No selection made.")
                continue
            try:
                selected_indices = [int(x.strip()) for x in selected.split(",") if x.strip().isdigit()]
            except Exception:
                print("Invalid input.")
                continue
            selected_ids = [emails_info[i-1]["id"] for i in selected_indices if 1 <= i <= len(emails_info)]
            if not selected_ids:
                print("No valid email numbers selected.")
                continue
            
            # Retrieve and display the new emails
            emails = retrieve_emails_by_ids(selected_ids, headers, target_user)
            if not emails:
                print("\nNo emails were retrieved.")
                
        elif choice == "2":
            # Fetch fresh email list
            print("\nFetching fresh email list...")
            fetch_last_email_ids(headers, limit=limit)
            email_ids = get_cached_email_ids(limit=limit)
            emails_info = []
            
            for eid in email_ids:
                url = f"https://graph.microsoft.com/v1.0/users/{target_user}/messages/{eid}?$select=id,subject"
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        emails_info.append({"id": data.get("id"), "subject": data.get("subject", "No Subject")})
                except Exception:
                    continue
            
            if not emails_info:
                print("No recent emails found.")
                continue
                
            print("\nUpdated Recent Emails:")
            print("=" * 60)
            for idx, info in enumerate(emails_info, 1):
                print(f"{idx}. ID: {info['id']}")
                print(f"   Subject: {info['subject']}")
            print("=" * 60)
            
            print("Enter the numbers of the emails you want to retrieve (comma-separated, e.g., 1,3,5): ", end="")
            selected = input().strip()
            if not selected:
                print("No selection made.")
                continue
            try:
                selected_indices = [int(x.strip()) for x in selected.split(",") if x.strip().isdigit()]
            except Exception:
                print("Invalid input.")
                continue
            selected_ids = [emails_info[i-1]["id"] for i in selected_indices if 1 <= i <= len(emails_info)]
            if not selected_ids:
                print("No valid email numbers selected.")
                continue
            
            # Retrieve and display the new emails
            emails = retrieve_emails_by_ids(selected_ids, headers, target_user)
            if not emails:
                print("\nNo emails were retrieved.")
                
        elif choice == "3":
            print("\n👋 Goodbye! Thank you for using the Email By ID Retriever.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")                                 

if __name__ == "__main__":
    main() 