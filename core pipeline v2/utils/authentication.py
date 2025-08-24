import os
import requests
from typing import Dict, Any
from settings import CLIENT_ID, TENANT_ID, CLIENT_SECRET, GRAPH_API_BASE


class OneDriveAuth:
    def __init__(self):
        self.access_token = None
        self._get_access_token()

    def _get_access_token(self):
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
        else:
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")

    def get_headers(self) -> Dict[str, str]:
        if not self.access_token:
            self._get_access_token()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }


def get_shared_files_token() -> str:
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access_token')
    else:
        raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_datetime(datetime_str: str) -> str:
    if not datetime_str or datetime_str == "Unknown":
        return "Unknown"
    
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return datetime_str
