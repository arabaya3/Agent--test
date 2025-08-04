import os
import requests
import json
from dotenv import load_dotenv
import msal

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

def retrieve_emails_by_ids(email_ids):
    print("============================================================")
    print("Email ID Retriever")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    emails = []
    
    for i, email_id in enumerate(email_ids, 1):
        print(f"Retrieving email {i}/{len(email_ids)}: {email_id}")
        
        email_data = get_email_by_id(email_id, headers)
        if email_data:
            email_info = {
                "id": email_data.get("id"),
                "subject": email_data.get("subject", "No Subject"),
                "from": email_data.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "receivedDateTime": email_data.get("receivedDateTime"),
                "hasAttachments": email_data.get("hasAttachments", False),
                "bodyPreview": email_data.get("bodyPreview", "")[:100] + "..." if email_data.get("bodyPreview") else "No preview"
            }
            emails.append(email_info)
            print(f"✓ Retrieved: {email_info['subject']}")
        else:
            print(f"✗ Failed to retrieve email {email_id}")
    
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total emails requested: {len(email_ids)}")
    print(f"Successfully retrieved: {len(emails)}")
    print(f"Failed: {len(email_ids) - len(emails)}")
    
    if emails:
        print("\nRetrieved Emails:")
        print("============================================================")
        for i, email in enumerate(emails, 1):
            print(f"{i}. Subject: {email['subject']}")
            print(f"   From: {email['from']}")
            print(f"   Date: {email['receivedDateTime']}")
            print(f"   Has Attachments: {'Yes' if email['hasAttachments'] else 'No'}")
            print(f"   Preview: {email['bodyPreview']}")
            print()
    
    return emails

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