import os
import requests
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

_email_id_cache = []

def fetch_last_email_ids(headers, limit=100, user_id=None):
    """Fetch and cache the last N email IDs (up to 100)."""
    global _email_id_cache
    limit = min(max(1, int(limit)), 100)
    
    # For application permissions, we need to specify a user ID
    if user_id:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages?$top={limit}&$select=id&$orderby=receivedDateTime desc"
    else:
        # Fallback to /me for backward compatibility
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