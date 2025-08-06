import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import msal
from urllib.parse import quote
import time
from shared_email_ids import fetch_last_email_ids, get_cached_email_ids, get_access_token

load_dotenv()

def get_access_token():
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    
    if not client_id or not tenant_id:
        print("Error: CLIENT_ID and TENANT_ID must be set in .env file")
        return None
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.PublicClientApplication(client_id, authority=authority)
    
    scopes = ["https://graph.microsoft.com/.default"]
    
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print("Error: Failed to create device flow")
        return None
    
    print("============================================================")
    print("Email ID Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def get_email_by_id(email_id, headers):
    url = f"https://graph.microsoft.com/v1.0/me/messages/{email_id}"
    
    try:
        print(f"[DEBUG] Requesting email: {url}")
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

def get_conversation_messages(conversation_id, headers):
    from urllib.parse import quote
    import time
    base_url = "https://graph.microsoft.com/v1.0"
    
    # 1. Try $search (if enabled)
    search_url = f"{base_url}/me/messages?$search=\"conversationId:{conversation_id}\""
    print(f"[DEBUG] Requesting ($search): {search_url}")
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                print(f"[DEBUG] Found {len(messages)} messages using $search.")
                return messages
            else:
                print(f"[DEBUG] No messages found using $search for conversationId: {conversation_id}")
        else:
            print(f"[DEBUG] Status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving conversation ($search) {conversation_id}: {e}")
    
    # 2. Try msgfolderroot (AllItems) with smaller limit
    allitems_url = (
        f"{base_url}/me/mailFolders/msgfolderroot/messages?"
        f"$filter=conversationId eq '{conversation_id}'&$orderby=sentDateTime asc&$top=50"
    )
    print(f"[DEBUG] Requesting (msgfolderroot): {allitems_url}")
    try:
        response = requests.get(allitems_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                print(f"[DEBUG] Found {len(messages)} messages in msgfolderroot.")
                return messages
            else:
                print(f"[DEBUG] No messages found in msgfolderroot for conversationId: {conversation_id}")
        else:
            print(f"[DEBUG] Status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving conversation (msgfolderroot) {conversation_id}: {e}")
    
    # 3. Try inbox with smaller limit
    inbox_url = (
        f"{base_url}/me/mailFolders/inbox/messages?"
        f"$filter=conversationId eq '{conversation_id}'&$orderby=sentDateTime asc&$top=50"
    )
    print(f"[DEBUG] Requesting (inbox): {inbox_url}")
    try:
        response = requests.get(inbox_url, headers=headers, timeout=30)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            if messages:
                print(f"[DEBUG] Found {len(messages)} messages in inbox.")
                return messages
            else:
                print(f"[DEBUG] No messages found in inbox for conversationId: {conversation_id}")
        else:
            print(f"[DEBUG] Status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving conversation (inbox) {conversation_id}: {e}")
    
    # 4. Limited fallback: Fetch recent messages only (max 1000)
    print(f"[DEBUG] Trying limited fallback: fetching recent messages only...")
    all_msgs = []
    next_url = f"{base_url}/me/messages?$top=100&$orderby=receivedDateTime desc"
    message_count = 0
    max_messages = 100  # Limit to 100 messages only
    
    while next_url and message_count < max_messages:
        print(f"[DEBUG] Requesting (limited): {next_url}")
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
                    time.sleep(0.1)  # Reduced delay
            else:
                print(f"[DEBUG] Status {response.status_code}: {response.text}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving messages for client-side filtering: {e}")
            break
    
    if all_msgs:
        print(f"[DEBUG] Found {len(all_msgs)} messages by limited fallback (searched {message_count} recent messages).")
        all_msgs.sort(key=lambda m: m.get("sentDateTime", ""))
        return all_msgs
    
    print(f"[DEBUG] All attempts failed for conversationId: {conversation_id}")
    print(f"[DEBUG] Conversation not found in recent {message_count} messages.")
    return []

def get_recent_email_ids(headers, limit=10):
    """Helper function to get recent email IDs for testing"""
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}&$select=id,subject,from,receivedDateTime&$orderby=receivedDateTime desc"
    
    try:
        print(f"[DEBUG] Getting recent email IDs...")
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
    print(f"[DEBUG] Found {len(emails)} emails from {len(email_ids)} recent emails.")
    return emails

def retrieve_emails_by_ids(email_ids, headers):
    print("============================================================")
    print("Email ID Retriever (with Conversation Thread)")
    print("============================================================")
    
    exclude_original = None
    while exclude_original not in ("y", "n"):
        exclude_original = input("Exclude the original message and only show replies? (y/n): ").strip().lower()
    exclude_original = exclude_original == "y"
    
    all_conversation_emails = []
    
    for i, email_id in enumerate(email_ids, 1):
        print(f"Retrieving email {i}/{len(email_ids)}: {email_id}")
        email_data = get_email_by_id(email_id, headers)
        if not email_data:
            print(f"✗ Failed to retrieve email {email_id}")
            continue
        conversation_id = email_data.get("conversationId")
        if not conversation_id:
            print(f"✗ No conversationId found for email {email_id}")
            continue
        conversation_messages = get_conversation_messages(conversation_id, headers)
        if not conversation_messages:
            print(f"✗ No messages found in conversation {conversation_id}")
            continue
        # Combine the original email and all conversation messages, remove duplicates by ID, and sort by receivedDateTime
        orig_id = str(email_data.get("id")).lower()
        # Build a dict to deduplicate by ID
        msg_dict = {orig_id: {
            "id": email_data.get("id"),
            "subject": email_data.get("subject", "No Subject"),
            "from": email_data.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email_data.get("receivedDateTime"),
            "hasAttachments": email_data.get("hasAttachments", False),
            "bodyPreview": (email_data.get("bodyPreview", "")[:100] + "..." if email_data.get("bodyPreview") else "No preview"),
            "conversationId": email_data.get("conversationId")
        }}
        for msg in conversation_messages:
            msg_id = str(msg.get("id")).lower()
            if msg_id not in msg_dict:
                msg_dict[msg_id] = {
                    "id": msg.get("id"),
                    "subject": msg.get("subject", "No Subject"),
                    "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "receivedDateTime": msg.get("receivedDateTime"),
                    "hasAttachments": msg.get("hasAttachments", False),
                    "bodyPreview": (msg.get("bodyPreview", "")[:100] + "..." if msg.get("bodyPreview") else "No preview"),
                    "conversationId": msg.get("conversationId")
                }
        # Sort all messages by receivedDateTime
        output_msgs = sorted(msg_dict.values(), key=lambda m: m.get("receivedDateTime", ""))
        all_conversation_emails.extend(output_msgs)
        print(f"✓ Retrieved {len(output_msgs)} message(s) in conversation.")
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total conversations requested: {len(email_ids)}")
    print(f"Total messages retrieved: {len(all_conversation_emails)}")
    if all_conversation_emails:
        print("\nRetrieved Conversation Messages:")
        print("============================================================")
        for i, email in enumerate(all_conversation_emails, 1):
            print(f"{i}. Subject: {email['subject']}")
            print(f"   From: {email['from']}")
            print(f"   Date: {email['receivedDateTime']}")
            print(f"   Has Attachments: {'Yes' if email['hasAttachments'] else 'No'}")
            print(f"   Preview: {email['bodyPreview']}")
            print(f"   ConversationId: {email['conversationId']}")
            print()
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
    # Fetch subjects for the recent emails
    emails_info = []
    for eid in email_ids:
        url = f"https://graph.microsoft.com/v1.0/me/messages/{eid}?$select=id,subject"
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
    emails = retrieve_emails_by_ids(selected_ids, headers)
    
    # If no emails found, offer to show recent emails again
    if not emails:
        print("\nNo emails were retrieved. Would you like to see recent email IDs to try again? (y/n): ", end="")
        retry = input().strip().lower()
        if retry == 'y':
            get_recent_email_ids(headers, 10)

if __name__ == "__main__":
    main() 