import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
import time
from .shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from shared.auth import get_access_token

load_dotenv()

def get_conversation_messages(conversation_id, headers, user_id=None):
    from urllib.parse import quote
    import time
    base_url = "https://graph.microsoft.com/v1.0"
    
    # For application permissions, we need to specify a user ID
    if user_id:
        user_prefix = f"users/{user_id}"
    else:
        user_prefix = "me"
    
    # 1. Try $search (if enabled)
    search_url = f"{base_url}/{user_prefix}/messages?$search=\"conversationId:{conversation_id}\""
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
        f"{base_url}/{user_prefix}/mailFolders/msgfolderroot/messages?"
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
        f"{base_url}/{user_prefix}/mailFolders/inbox/messages?"
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
    next_url = f"{base_url}/{user_prefix}/messages?$top=100&$orderby=receivedDateTime desc"
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

def search_emails_by_subject_and_date_range(subject, start_date, end_date, headers, email_ids, user_id=None):
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return []
    
    filtered_emails = []
    for eid in email_ids:
        if user_id:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{eid}"
        else:
            url = f"https://graph.microsoft.com/v1.0/me/messages/{eid}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                email = response.json()
                email_date = email.get("receivedDateTime", "")
                email_subject = email.get("subject", "")
                if start_datetime <= email_date <= end_datetime and subject.lower() in email_subject.lower():
                    filtered_emails.append(email)
            else:
                continue
        except Exception:
            continue
    print(f"[DEBUG] Found {len(filtered_emails)} emails matching subject and date from {len(email_ids)} recent emails.")
    return filtered_emails

def retrieve_emails_by_subject_date_range(subject, start_date, end_date, headers, email_ids, user_id=None):
    print("============================================================")
    print("Email Subject-Date Range Retriever (with Conversation Thread)")
    print("============================================================")
    print(f"Searching for emails with subject containing: {subject}")
    print(f"Date range: {start_date} to {end_date}")
    print("============================================================")
    
    emails = search_emails_by_subject_and_date_range(subject, start_date, end_date, headers, email_ids, user_id)
    
    if not emails:
        print("No emails found matching the criteria.")
        return []
    
    print(f"\nFound {len(emails)} emails with subject '{subject}' in date range {start_date} to {end_date}")
    print("============================================================")
    
    # Always include main email and all replies (no user prompt needed)
    all_conversation_emails = []
    processed_conversation_ids = set()  # Track processed conversations to avoid duplicates
    unique_conversations_processed = 0  # Count unique conversations actually processed
    
    for i, email in enumerate(emails, 1):
        print(f"\nProcessing email {i}/{len(emails)}: {email.get('subject', 'No Subject')}")
        conversation_id = email.get("conversationId")
        if not conversation_id:
            print(f"✗ No conversationId found for email")
            continue
            
        # Skip if we've already processed this conversation
        if conversation_id in processed_conversation_ids:
            print(f"✗ Conversation already processed, skipping")
            continue
        processed_conversation_ids.add(conversation_id)
        unique_conversations_processed += 1
        
        conversation_messages = get_conversation_messages(conversation_id, headers, user_id)
        if not conversation_messages:
            print(f"✗ No messages found in conversation {conversation_id}")
            continue
            
        # Build a dict to deduplicate by ID (include original email and all conversation messages)
        msg_dict = {}
        
        # Add the original email first
        orig_id = str(email.get("id")).lower()
        msg_dict[orig_id] = {
            "id": email.get("id"),
            "subject": email.get("subject", "No Subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email.get("receivedDateTime"),
            "hasAttachments": email.get("hasAttachments", False),
            "bodyPreview": (email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"),
            "conversationId": email.get("conversationId")
        }
        
        # Add all conversation messages (this will overwrite the original if it's duplicated)
        for msg in conversation_messages:
            msg_id = str(msg.get("id")).lower()
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
        print(f"✓ Retrieved {len(output_msgs)} message(s) in conversation (including main email and all replies).")
    
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Subject keyword: {subject}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total emails found: {len(emails)}")
    print(f"Unique conversations processed: {unique_conversations_processed}")
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
    print("Email Subject Date Range Retriever")
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
    
    subject = input("Enter subject keyword to search: ").strip()
    if not subject:
        print("Error: Subject keyword is required")
        return
    
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if not start_date:
        print("Error: Start date is required")
        return
    
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    if not end_date:
        print("Error: End date is required")
        return
    
    emails = retrieve_emails_by_subject_date_range(subject, start_date, end_date, headers, email_ids)

if __name__ == "__main__":
    main() 