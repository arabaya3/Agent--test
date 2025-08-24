import os
import requests
from dotenv import load_dotenv
try:
    from shared.auth import get_access_token
except ImportError:
    # Allow running email tools directly as scripts
    import sys, importlib.util
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Core_Pipline
    auth_path = os.path.join(base_dir, 'shared', 'auth.py')
    spec = importlib.util.spec_from_file_location('shared.auth', auth_path)
    if spec and spec.loader:
        _mod = importlib.util.module_from_spec(spec)
        sys.modules['shared.auth'] = _mod
        spec.loader.exec_module(_mod)
        get_access_token = _mod.get_access_token
    else:
        raise

load_dotenv()

_email_id_cache = []

def fetch_last_email_ids(headers, limit=100, user_id=None):
    global _email_id_cache
    limit = min(max(1, int(limit)), 100)
    
    # Prefer explicit user (supports application permissions). Fallback to DEFAULT_USER_ID env, else /me
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if target_user:
        url = f"https://graph.microsoft.com/v1.0/users/{target_user}/messages?$top={limit}&$select=id&$orderby=receivedDateTime desc"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}&$select=id&$orderby=receivedDateTime desc"
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        _email_id_cache = [msg['id'] for msg in data.get('value', []) if 'id' in msg]
                                                                   
    except Exception as e:
        print(f"[ERROR] Could not fetch email IDs: {e}")
        _email_id_cache = []

def get_cached_email_ids(limit=100):
    limit = min(max(1, int(limit)), 100)
    return _email_id_cache[:limit]