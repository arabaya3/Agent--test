import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import msal
from urllib.parse import quote

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
    print("Email Sender-Date Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
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
    max_messages = 1000  # Limit to prevent excessive API calls
    
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

def search_emails_by_sender_date(sender, date, headers):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_date = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_date = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return []
    
    # Use client-side filtering to avoid InefficientFilter errors
    print(f"[DEBUG] Fetching recent emails and filtering client-side...")
    all_emails = []
    next_url = "https://graph.microsoft.com/v1.0/me/messages?$top=100&$orderby=receivedDateTime desc"
    message_count = 0
    max_messages = 2000  # Limit to prevent excessive API calls
    
    while next_url and message_count < max_messages:
        try:
            print(f"[DEBUG] Fetching batch {message_count//100 + 1}...")
            response = requests.get(next_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                batch = data.get("value", [])
                all_emails.extend(batch)
                message_count += len(batch)
                next_url = data.get("@odata.nextLink")
                
                print(f"[DEBUG] Retrieved {len(batch)} emails (Total: {len(all_emails)})")
                
                # Check if we have enough emails to cover the date range
                if batch:
                    earliest_date = batch[-1].get("receivedDateTime", "")
                    if earliest_date < start_date:
                        print(f"[DEBUG] Reached emails older than search date. Stopping search.")
                        break
            else:
                print(f"[DEBUG] Failed to fetch emails: {response.status_code}")
                print(f"[DEBUG] Response: {response.text}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Error fetching emails: {e}")
            break
    
    # Filter emails by sender and date
    print(f"[DEBUG] Filtering {len(all_emails)} emails by sender '{sender}' and date '{date}'...")
    filtered_emails = []
    
    for email in all_emails:
        email_sender = email.get("from", {}).get("emailAddress", {}).get("address", "")
        email_date = email.get("receivedDateTime", "")
        
        # Check if sender matches (case-insensitive)
        if email_sender.lower() == sender.lower():
            # Check if date is in range
            if start_date <= email_date <= end_date:
                filtered_emails.append(email)
    
    print(f"[DEBUG] Found {len(filtered_emails)} emails matching criteria")
    return filtered_emails

def retrieve_emails_by_sender_date(sender, date, headers):
    print("============================================================")
    print("Email Sender-Date Retriever (with Conversation Thread)")
    print("============================================================")
    print(f"Searching for emails from: {sender}")
    print(f"Date: {date}")
    print("============================================================")
    
    emails = search_emails_by_sender_date(sender, date, headers)
    
    if not emails:
        print("No emails found matching the criteria.")
        return []
    
    print(f"\nFound {len(emails)} emails from {sender} on {date}")
    print("============================================================")
    
    exclude_original = None
    while exclude_original not in ("y", "n"):
        exclude_original = input("Exclude the original message and only show replies? (y/n): ").strip().lower()
    exclude_original = exclude_original == "y"
    
    all_conversation_emails = []
    
    for i, email in enumerate(emails, 1):
        print(f"\nProcessing email {i}/{len(emails)}: {email.get('subject', 'No Subject')}")
        conversation_id = email.get("conversationId")
        if not conversation_id:
            print(f"✗ No conversationId found for email")
            continue
        conversation_messages = get_conversation_messages(conversation_id, headers)
        if not conversation_messages:
            print(f"✗ No messages found in conversation {conversation_id}")
            continue
        # Combine the original email and all conversation messages, remove duplicates by ID, and sort by receivedDateTime
        orig_id = str(email.get("id")).lower()
        # Build a dict to deduplicate by ID
        msg_dict = {orig_id: {
            "id": email.get("id"),
            "subject": email.get("subject", "No Subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email.get("receivedDateTime"),
            "hasAttachments": email.get("hasAttachments", False),
            "bodyPreview": (email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"),
            "conversationId": email.get("conversationId")
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
    print(f"Sender: {sender}")
    print(f"Date: {date}")
    print(f"Total conversations found: {len(emails)}")
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
    print("Email Sender-Date Retriever")
    print("============================================================")
    
    # First, get access token
    access_token = get_access_token()
    if not access_token:
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sender = input("Enter sender email address: ").strip()
    if not sender:
        print("Error: Sender email is required")
        return
    
    date = input("Enter date (YYYY-MM-DD): ").strip()
    if not date:
        print("Error: Date is required")
        return
    
    emails = retrieve_emails_by_sender_date(sender, date, headers)

if __name__ == "__main__":
    main() 