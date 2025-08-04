import os
import requests
import json
from datetime import datetime
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

def search_emails_by_sender_date(sender, date, headers):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_date = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_date = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return []
    
    filter_query = f"from/emailAddress/address eq '{sender}' and receivedDateTime ge {start_date} and receivedDateTime le {end_date}"
    
    url = f"https://graph.microsoft.com/v1.0/me/messages?$filter={filter_query}&$orderby=receivedDateTime desc"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching emails: {e}")
        return []

def retrieve_emails_by_sender_date(sender, date):
    print("============================================================")
    print("Email Sender-Date Retriever")
    print("============================================================")
    print(f"Searching for emails from: {sender}")
    print(f"Date: {date}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    emails = search_emails_by_sender_date(sender, date, headers)
    
    if not emails:
        print("No emails found matching the criteria.")
        return []
    
    print(f"\nFound {len(emails)} emails from {sender} on {date}")
    print("============================================================")
    
    email_list = []
    for i, email in enumerate(emails, 1):
        email_info = {
            "id": email.get("id"),
            "subject": email.get("subject", "No Subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
            "receivedDateTime": email.get("receivedDateTime"),
            "hasAttachments": email.get("hasAttachments", False),
            "bodyPreview": email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"
        }
        email_list.append(email_info)
        
        print(f"{i}. Subject: {email_info['subject']}")
        print(f"   From: {email_info['from']}")
        print(f"   Date: {email_info['receivedDateTime']}")
        print(f"   Has Attachments: {'Yes' if email_info['hasAttachments'] else 'No'}")
        print(f"   Preview: {email_info['bodyPreview']}")
        print()
    
    print("============================================================")
    print("Search Summary")
    print("============================================================")
    print(f"Sender: {sender}")
    print(f"Date: {date}")
    print(f"Emails found: {len(email_list)}")
    
    return email_list

def main():
    print("============================================================")
    print("Email Sender-Date Retriever")
    print("============================================================")
    
    sender = input("Enter sender email address: ").strip()
    if not sender:
        print("Error: Sender email is required")
        return
    
    date = input("Enter date (YYYY-MM-DD): ").strip()
    if not date:
        print("Error: Date is required")
        return
    
    emails = retrieve_emails_by_sender_date(sender, date)
    
    if emails:
        print("\n============================================================")
        print("Full Email Data (JSON)")
        print("============================================================")
        print(json.dumps(emails, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 