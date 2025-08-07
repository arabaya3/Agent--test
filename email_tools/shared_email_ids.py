import os
import requests
from dotenv import load_dotenv
import msal

load_dotenv()

_email_id_cache = []


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
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def fetch_last_email_ids(headers, limit=100):
    """Fetch and cache the last N email IDs (up to 100)."""
    global _email_id_cache
    limit = min(max(1, int(limit)), 100)
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}&$select=id&$orderby=receivedDateTime desc"
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        _email_id_cache = [msg['id'] for msg in data.get('value', []) if 'id' in msg]
        # print(f"[INFO] Cached {len(_email_id_cache)} email IDs.")
    except Exception as e:
        print(f"[ERROR] Could not fetch email IDs: {e}")
        _email_id_cache = []

def get_cached_email_ids(limit=100):
    """Return up to 'limit' cached email IDs."""
    limit = min(max(1, int(limit)), 100)
    return _email_id_cache[:limit]