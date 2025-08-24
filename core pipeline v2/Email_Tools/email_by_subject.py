import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_emails_by_subject(subject_query: str) -> str:
    """Search emails by subject and return formatted results as string."""

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
    result.append(f"=== Email Search Results for: '{subject_query}' ===\n")

    try:
        # Get access token
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
        result.append("✓ Authentication successful\n")

        # Search emails
        api_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages"
        params = {
            '$filter': f"contains(subject,'{subject_query}')",
            '$select': 'id,subject,from,receivedDateTime,bodyPreview,hasAttachments,isRead,toRecipients',
            '$orderby': 'receivedDateTime desc',
            '$top': 20
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(api_url, params=params, headers=headers)

        # Handle errors with fallback to search
        if response.status_code >= 400:
            try:
                err = response.json()
                err_code = err.get('error', {}).get('code', '')
                if 'InefficientFilter' in err_code or response.status_code == 400:
                    # Fallback to search
                    result.append("⚠ Fallback to search method...\n")
                    api_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages"
                    params = {
                        '$search': f'"subject:{subject_query}"',
                        '$select': 'id,subject,from,receivedDateTime,bodyPreview,hasAttachments,isRead,toRecipients',
                        '$top': 20
                    }
                    headers['ConsistencyLevel'] = 'eventual'
                    response = requests.get(api_url, params=params, headers=headers)

                if response.status_code >= 400:
                    err_msg = err.get('error', {}).get('message', response.text)
                    return f"ERROR: API request failed - {response.status_code}: {err_msg}"
            except:
                return f"ERROR: Request failed - {response.status_code}: {response.text}"

        data = response.json()
        emails = data.get('value', [])

        result.append(f"Found {len(emails)} emails:\n")
        result.append("=" * 60 + "\n")

        # Format results
        for i, email in enumerate(emails, 1):
            from_addr = email.get('from', {}).get('emailAddress', {})
            to_list = [r.get('emailAddress', {}).get('address', '')
                      for r in email.get('toRecipients', [])]

            result.append(f"Email {i}")
            result.append(f"Subject: {email.get('subject', 'No Subject')}")
            result.append(f"From: {from_addr.get('name', 'Unknown')} <{from_addr.get('address', '')}>")
            result.append(f"To: {', '.join(to_list[:3])}{'...' if len(to_list) > 3 else ''}")
            result.append(f"Date: {email.get('receivedDateTime', '')}")
            preview = email.get('bodyPreview', '')
            result.append(f"Preview: {preview}")

        # Show recent emails if no matches
        if len(emails) == 0:
            result.append("\n No matches found. Recent inbox emails:")
            try:
                recent_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages"
                recent_params = {'$select': 'subject', '$top': 5}
                recent_resp = requests.get(recent_url, params=recent_params,
                                         headers={'Authorization': f'Bearer {access_token}'})
                if recent_resp.status_code == 200:
                    recent_emails = recent_resp.json().get('value', [])
                    for j, email in enumerate(recent_emails, 1):
                        result.append(f"{j}. {email.get('subject', 'No Subject')}")
            except:
                result.append("Could not retrieve recent emails")

        return "\n".join(result)

    except Exception as e:
        return f"ERROR: {str(e)}"
 