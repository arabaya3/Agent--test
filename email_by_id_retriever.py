import os
import requests
import json
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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
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
        response = requests.get(search_url, headers=headers)
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
    # 2. Try msgfolderroot (AllItems)
    allitems_url = (
        f"{base_url}/me/mailFolders/msgfolderroot/messages?"
        f"$filter=conversationId eq '{conversation_id}'&$orderby=sentDateTime asc"
    )
    print(f"[DEBUG] Requesting (msgfolderroot): {allitems_url}")
    try:
        response = requests.get(allitems_url, headers=headers)
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
    # 3. Fallback: Fetch all messages and filter client-side (paginated)
    print(f"[DEBUG] Fetching all messages and filtering client-side. This may take a while...")
    all_msgs = []
    next_url = f"{base_url}/me/messages?$top=100"
    while next_url:
        print(f"[DEBUG] Requesting (all): {next_url}")
        try:
            response = requests.get(next_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                batch = data.get("value", [])
                filtered = [m for m in batch if m.get("conversationId") == conversation_id]
                all_msgs.extend(filtered)
                next_url = data.get("@odata.nextLink")
                if next_url:
                    time.sleep(0.2)  # Be gentle to avoid throttling
            else:
                print(f"[DEBUG] Status {response.status_code}: {response.text}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving all messages for client-side filtering: {e}")
            break
    if all_msgs:
        print(f"[DEBUG] Found {len(all_msgs)} messages by client-side filtering.")
        all_msgs.sort(key=lambda m: m.get("sentDateTime", ""))
        return all_msgs
    print(f"[DEBUG] All attempts failed for conversationId: {conversation_id}")
    return []

def retrieve_emails_by_ids(email_ids):
    print("============================================================")
    print("Email ID Retriever (with Conversation Thread)")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
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
        # Sort by sentDateTime
        conversation_messages.sort(key=lambda m: m.get("sentDateTime", ""))
        # Optionally exclude the original message
        if exclude_original:
            conversation_messages = [m for m in conversation_messages if m.get("id") != email_id]
        # Prepare output
        for msg in conversation_messages:
            email_info = {
                "id": msg.get("id"),
                "subject": msg.get("subject", "No Subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "receivedDateTime": msg.get("receivedDateTime"),
                "hasAttachments": msg.get("hasAttachments", False),
                "bodyPreview": (msg.get("bodyPreview", "")[:100] + "..." if msg.get("bodyPreview") else "No preview"),
                "conversationId": msg.get("conversationId")
            }
            all_conversation_emails.append(email_info)
        print(f"✓ Retrieved {len(conversation_messages)} message(s) in conversation.")
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
    print("Email ID Retriever")
    print("============================================================")
    print("Enter email IDs (one per line, press Enter twice when done):")
    
    email_ids = []
    while True:
        email_id = input().strip()
        if not email_id:
            break
        email_ids.append(email_id)
    
    if not email_ids:
        print("No email IDs provided.")
        return
    
    emails = retrieve_emails_by_ids(email_ids)
    
    if emails:
        print("\n============================================================")
        print("Full Email Data (JSON)")
        print("============================================================")
        print(json.dumps(emails, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 