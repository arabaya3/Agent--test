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


def list_shared_files_delegated_only(data: Dict[str, Any]) -> str:
    top = data.get("top", DEFAULT_TOP_LIMIT)
    cache_path = data.get("cache_path", ".msal_token_cache.bin")
    
    result = [f"=== Shared Text Files Only ===\n"]

    try:
        result.append("Acquiring delegated permissions token automatically...\n")
        
        client_id = os.getenv("PUBLIC_CLIENT_ID") or os.getenv("CLIENT_ID")
        tenant_id = os.getenv("TENANT_ID")
        username = os.getenv("GRAPH_USERNAME")
        password = os.getenv("GRAPH_PASSWORD")
        
        if not client_id:
            raise RuntimeError("PUBLIC_CLIENT_ID (or CLIENT_ID) must be set for delegated auth.")
        if not tenant_id:
            raise RuntimeError("TENANT_ID must be set for delegated auth.")
        if not username or not password:
            raise RuntimeError("GRAPH_USERNAME and GRAPH_PASSWORD must be set in .env file.")
        
        try:
            import msal
        except ImportError:
            os.system("pip install msal")
            import msal

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        env_scopes = os.getenv("DELEGATED_SCOPES")
        if env_scopes:
            scopes = [s for s in env_scopes.replace(",", " ").split() if s]
        else:
            scopes = ["Files.Read", "offline_access"]

        if not cache_path:
            token_cache, cache_file = None, None
        else:
            cache_file = Path(cache_path)
            try:
                token_cache = msal.SerializableTokenCache()
                if cache_file.exists():
                    try:
                        token_cache.deserialize(cache_file.read_text(encoding="utf-8"))
                    except Exception:
                        pass
            except Exception:
                token_cache, cache_file = None, None

        app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=token_cache)

        try:
            accounts = app.get_accounts()
            if accounts:
                result_auth = app.acquire_token_silent(scopes, account=accounts[0])
                if isinstance(result_auth, dict) and "access_token" in result_auth:
                    if token_cache and cache_file:
                        try:
                            cache_file.write_text(token_cache.serialize(), encoding="utf-8")
                        except Exception:
                            pass
                    result.append("Using cached token for authentication\n")
                    access_token = result_auth["access_token"]
                else:
                    raise Exception("Silent token acquisition failed")
            else:
                raise Exception("No cached accounts found")
        except Exception:
            try:
                result.append("Attempting username/password authentication...\n")
                result_auth = app.acquire_token_by_username_password(username=username, password=password, scopes=scopes)
                if "access_token" in result_auth:
                    if token_cache and cache_file:
                        try:
                            cache_file.write_text(token_cache.serialize(), encoding="utf-8")
                        except Exception:
                            pass
                    result.append("Username/password authentication successful!\n")
                    access_token = result_auth["access_token"]
                else:
                    raise Exception("Username/password authentication failed")
            except Exception as e:
                raise RuntimeError(f"Authentication failed: {str(e)}")
        
        result.append("Delegated authentication successful!\n")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        url = f"{GRAPH_API_BASE}/me/drive/sharedWithMe?$top=200"
        all_items = []
        
        while url:
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
            if response.status_code >= 400:
                try:
                    err = response.json()
                    err_msg = err.get('error', {}).get('message', response.text)
                    return f"ERROR: API request failed - {response.status_code}: {err_msg}"
                except:
                    return f"ERROR: Request failed - {response.status_code}: {response.text}"

            data_response = response.json()
            page_items = data_response.get('value', [])
            all_items.extend(page_items)
            url = data_response.get('@odata.nextLink')

        text_files = []
        for item in all_items:
            remote = item.get("remoteItem") or {}
            name = item.get("name") or remote.get("name", "Unknown")
            is_folder = bool(item.get("folder") or remote.get("folder"))
            
            if not is_folder:
                file_extension = os.path.splitext(name.lower())[1]
                if file_extension in ['.txt', '.doc', '.docx', '.pdf']:
                    text_files.append(item)
                    if len(text_files) >= top:
                        break

        if not text_files:
            result.append("No shared text files found.")
            return "\n".join(result)

        result.append(f"Found {len(text_files)} shared text files:")
        result.append("=" * 80)

        for i, item in enumerate(text_files, 1):
            remote = item.get("remoteItem") or {}
            name = item.get("name") or remote.get("name", "Unknown")
            item_id = item.get("id") or remote.get("id", "Unknown")
            size = item.get("size") or remote.get("size", 0)
            last_modified = item.get("lastModifiedDateTime") or remote.get("lastModifiedDateTime", "Unknown")
            web_url = item.get("webUrl") or remote.get("webUrl", "")
            
            shared_by = "Unknown"
            shared_by_email = "Unknown"
            
            try:
                if remote.get("createdBy"):
                    created_by = remote.get("createdBy", {})
                    if created_by.get("user"):
                        shared_by = created_by["user"].get("displayName", created_by["user"].get("email", "Unknown"))
                        shared_by_email = created_by["user"].get("email", "Unknown")
                    else:
                        shared_by = created_by.get("displayName", "Unknown")
                elif item.get("createdBy"):
                    created_by = item.get("createdBy", {})
                    if created_by.get("user"):
                        shared_by = created_by["user"].get("displayName", created_by["user"].get("email", "Unknown"))
                        shared_by_email = created_by["user"].get("email", "Unknown")
                    else:
                        shared_by = created_by.get("displayName", "Unknown")
                elif remote.get("owner"):
                    owner = remote.get("owner", {})
                    if owner.get("user"):
                        shared_by = owner["user"].get("displayName", owner["user"].get("email", "Unknown"))
                        shared_by_email = owner["user"].get("email", "Unknown")
                    else:
                        shared_by = owner.get("displayName", "Unknown")
                elif item.get("owner"):
                    owner = item.get("owner", {})
                    if owner.get("user"):
                        shared_by = owner["user"].get("displayName", owner["user"].get("email", "Unknown"))
                        shared_by_email = owner["user"].get("email", "Unknown")
                    else:
                        shared_by = owner.get("displayName", "Unknown")
                
                if shared_by == "Unknown":
                    if web_url and "personal/" in web_url:
                        try:
                            url_parts = web_url.split("personal/")
                            if len(url_parts) > 1:
                                user_part = url_parts[1].split("/")[0]
                                if "_" in user_part:
                                    email_parts = user_part.split("_")
                                    if len(email_parts) >= 2:
                                        shared_by = f"{email_parts[0].title()} {email_parts[1].title()}"
                                        shared_by_email = user_part.replace("_", "@") + ".com"
                        except:
                            pass
                        
            except Exception as e:
                shared_by = f"Unknown (Error: {str(e)})"

            size_str = format_file_size(size)
            last_modified = format_datetime(last_modified)

            result.append(f"{i}. {name}")
            result.append(f"   ID: {item_id}")
            result.append(f"   Size: {size_str}")
            result.append(f"   Modified: {last_modified}")
            
            if shared_by != "Unknown" and shared_by_email != "Unknown":
                if shared_by != shared_by_email:
                    result.append(f"   Shared by: {shared_by} ({shared_by_email})")
                else:
                    result.append(f"   Shared by: {shared_by}")
            elif shared_by != "Unknown":
                result.append(f"   Shared by: {shared_by}")
            elif shared_by_email != "Unknown":
                result.append(f"   Shared by: {shared_by_email}")
            else:
                result.append(f"   Shared by: Unknown")
            
            if web_url:
                result.append(f"   URL: {web_url}")
            result.append("-" * 80)

        return "\n".join(result)

    except Exception as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    result = list_shared_files_delegated_only({"top": 5})
    print(result)
