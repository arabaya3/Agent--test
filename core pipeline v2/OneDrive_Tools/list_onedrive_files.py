import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import (
    USER_EMAIL, GRAPH_API_BASE, DEFAULT_TOP_LIMIT, 
    MAX_FILE_SIZE_DISPLAY, MAX_CONTENT_LENGTH,
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_DOCUMENT_EXTENSIONS,
    GRAPH_USERNAME, GRAPH_PASSWORD, DELEGATED_SCOPES, API_TIMEOUT, DEBUG
)
from utils import OneDriveAuth, format_file_size, format_datetime


def list_onedrive_files(folder_path: str = "", top: int = DEFAULT_TOP_LIMIT) -> str:
    auth = OneDriveAuth()
    result = []
    result.append(f"=== OneDrive Document Files in {folder_path if folder_path else 'Root'} ===\n")

    # Define supported document extensions
    supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.rtf', '.odt', '.ods', '.odp'}

    try:
        headers = auth.get_headers()
        result.append("Authentication successful\n")

        normalized_path = folder_path.replace("\\", "/").strip("/") if folder_path else ""
        
        if normalized_path:
            api_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/drive/root:/{normalized_path}:/children"
        else:
            api_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/drive/root/children"

        params = {'$top': min(200, top * 3)}  # Get more items to filter from
        items = []
        document_items = []
        
        while api_url and len(document_items) < top:
            response = requests.get(api_url, params=params, headers=headers, timeout=API_TIMEOUT)

            if response.status_code >= 400:
                try:
                    err = response.json()
                    err_msg = err.get('error', {}).get('message', response.text)
                    if response.status_code == 404 and "not found" in err_msg.lower():
                        return f"ERROR: Folder path '{folder_path}' not found"
                    return f"ERROR: API request failed - {response.status_code}: {err_msg}"
                except:
                    return f"ERROR: Request failed - {response.status_code}: {response.text}"

            data_response = response.json()
            page_items = data_response.get('value', [])
            
            for item in page_items:
                # Only include files (not folders) with supported extensions
                if not item.get('folder'):
                    file_name = item.get('name', '')
                    file_extension = Path(file_name).suffix.lower()
                    if file_extension in supported_extensions:
                        document_items.append(item)
                        if len(document_items) >= top:
                            break
                
                items.append(item)
            
            if len(document_items) >= top:
                break
                
            api_url = data_response.get('@odata.nextLink') if len(document_items) < top else None
            params = {}

        if not document_items:
            result.append("No document files found in the specified location.")
            result.append(f"Supported extensions: {', '.join(sorted(supported_extensions))}")
            return "\n".join(result)

        result.append(f"Found {len(document_items)} document files:")
        result.append(f"Supported extensions: {', '.join(sorted(supported_extensions))}")
        result.append("=" * 80)

        for i, item in enumerate(document_items, 1):
            name = item.get('name', 'Unknown')
            item_id = item.get('id', 'Unknown')
            size = item.get('size', 0)
            last_modified = item.get('lastModifiedDateTime', 'Unknown')
            web_url = item.get('webUrl', '')

            size_str = format_file_size(size)
            last_modified = format_datetime(last_modified)

            result.append(f"{i}. {name}")
            result.append(f"   ID: {item_id}")
            result.append(f"   Size: {size_str}")
            result.append(f"   Modified: {last_modified}")
            if web_url:
                result.append(f"   URL: {web_url}")
            result.append("-" * 80)

        return "\n".join(result)

    except Exception as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    result = list_onedrive_files(folder_path="", top=5)
    print(result)
