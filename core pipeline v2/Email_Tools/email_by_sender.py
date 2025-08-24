import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_emails_by_sender(sender: str) -> str:
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    user_email = os.getenv("DEFAULT_USER_ID")
    
    # Validate required environment variables
    if not all([tenant_id, client_id, client_secret, user_email]):
        missing_vars = []
        if not tenant_id: missing_vars.append("TENANT_ID")
        if not client_id: missing_vars.append("CLIENT_ID")
        if not client_secret: missing_vars.append("CLIENT_SECRET")
        if not user_email: missing_vars.append("DEFAULT_USER_ID")
        return f"ERROR: Missing required environment variables: {', '.join(missing_vars)}"

    result = []
    result.append(f"=== Emails from {sender} ===\n")

    try:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        token_resp = requests.post(token_url, data=token_data,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

        if token_resp.status_code != 200:
            error = token_resp.json()
            return f"ERROR: Auth failed - {error.get('error')}: {error.get('error_description')}"

        access_token = token_resp.json()['access_token']
        result.append("Authentication successful\n")

        api_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages"
        params = {
            '$select': 'id,subject,from,receivedDateTime,bodyPreview,hasAttachments,isRead,toRecipients,importance',
            '$orderby': 'receivedDateTime desc',
            '$top': 200
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(api_url, params=params, headers=headers)

        if response.status_code >= 400:
            try:
                err = response.json()
                err_msg = err.get('error', {}).get('message', response.text)
                return f"ERROR: API request failed - {response.status_code}: {err_msg}"
            except:
                return f"ERROR: Request failed - {response.status_code}: {response.text}"

        data = response.json()
        all_emails = data.get('value', [])

        emails = []
        sender_lower = sender.lower()
        
        for email in all_emails:
            from_info = email.get('from', {}).get('emailAddress', {})
            sender_email = from_info.get('address', '').lower()
            sender_name = from_info.get('name', '').lower()
            
            if (sender_lower == sender_email or 
                sender_lower in sender_name or 
                sender_name.startswith(sender_lower) or
                any(sender_lower in part for part in sender_name.split())):
                emails.append(email)

        if not emails:
            result.append(f"No emails found from sender: {sender}")
            return "\n".join(result)

        result.append(f"Found {len(emails)} emails:")
        result.append("=" * 80)

        for email in emails:
            from_addr = email.get('from', {}).get('emailAddress', {})
            to_list = [r.get('emailAddress', {}).get('address', '')
                      for r in email.get('toRecipients', [])]

            result.append(f"ID: {email.get('id', '')}")
            result.append(f"Subject: {email.get('subject', 'No Subject')}")
            result.append(f"From: {from_addr.get('name', 'Unknown')} <{from_addr.get('address', '')}>")
            result.append(f"To: {', '.join(to_list)}")
            result.append(f"Date: {email.get('receivedDateTime', '')}")
            result.append(f"Read: {email.get('isRead', False)}")
            result.append(f"Has Attachments: {email.get('hasAttachments', False)}")
            result.append(f"Importance: {email.get('importance', 'normal')}")
            result.append(f"Preview: {email.get('bodyPreview', '')}")
            result.append("-" * 80)

        return "\n".join(result)

    except Exception as e:
        return f"ERROR: {str(e)}"