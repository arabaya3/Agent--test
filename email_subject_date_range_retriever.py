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
    print("Email Subject-Date Range Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def search_emails_by_subject_date_range(subject, start_date, end_date, headers):
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return []
    
    subject_filter = f"contains(subject,'{subject}')"
    date_filter = f"receivedDateTime ge {start_datetime} and receivedDateTime le {end_datetime}"
    filter_query = f"{subject_filter} and {date_filter}"
    
    url = f"https://graph.microsoft.com/v1.0/me/messages?$filter={filter_query}&$orderby=receivedDateTime desc&$top=10"
    
    all_emails = []
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            emails = data.get("value", [])
            all_emails.extend(emails)
            
            print(f"Retrieved {len(emails)} emails... (Total: {len(all_emails)})")
            
            url = data.get("@odata.nextLink")
            
            if len(all_emails) >= 5000:
                print("Warning: Reached 5000 emails limit. Consider narrowing your search criteria.")
                break
                
    except requests.exceptions.RequestException as e:
        print(f"Error searching emails: {e}")
        return []
    
    return all_emails

def retrieve_emails_by_subject_date_range(subject, start_date, end_date):
    print("============================================================")
    print("Email Subject-Date Range Retriever")
    print("============================================================")
    print(f"Searching for emails with subject containing: {subject}")
    print(f"Date range: {start_date} to {end_date}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    emails = search_emails_by_subject_date_range(subject, start_date, end_date, headers)
    
    if not emails:
        print("No emails found matching the criteria.")
        return []
    
    print(f"\nFound {len(emails)} emails with subject '{subject}' in date range {start_date} to {end_date}")
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
    print(f"Subject keyword: {subject}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total emails found: {len(email_list)}")
    
    if email_list:
        date_counts = {}
        for email in email_list:
            date = email['receivedDateTime'][:10]
            date_counts[date] = date_counts.get(date, 0) + 1
        
        print("\nEmails per day:")
        for date in sorted(date_counts.keys()):
            print(f"  {date}: {date_counts[date]} emails")
    
    return email_list

def main():
    print("============================================================")
    print("Email Subject-Date Range Retriever")
    print("============================================================")
    
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
    
    emails = retrieve_emails_by_subject_date_range(subject, start_date, end_date)
    
    if emails:
        print("\n============================================================")
        print("Full Email Data (JSON)")
        print("============================================================")
        print(json.dumps(emails, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 