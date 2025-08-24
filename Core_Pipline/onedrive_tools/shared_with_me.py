import os
from typing import Optional, List, Dict, Any
import requests
from pathlib import Path
from io import BytesIO
import sys

# Import msal for delegated authentication
try:
    import msal
except ImportError:
    msal = None

try:
    from shared.auth import get_access_token
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from shared.auth import get_access_token

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def _get_token_cache(cache_path: Optional[str]):
    """Create or load a SerializableTokenCache if a cache_path is provided."""
    if not cache_path:
        return None, None
    cache_file = Path(cache_path)
    try:
        from msal import SerializableTokenCache  # type: ignore
        token_cache = SerializableTokenCache()
        if cache_file.exists():
            try:
                token_cache.deserialize(cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return token_cache, cache_file
    except Exception:
        return None, None


def _save_token_cache(token_cache, cache_file: Optional[Path]):
    if token_cache and cache_file:
        try:
            cache_file.write_text(token_cache.serialize(), encoding="utf-8")
        except Exception:
            pass


def _acquire_delegated_token_via_device_code(scopes: Optional[List[str]] = None, cache_path: Optional[str] = None) -> str:
    client_id = os.getenv("PUBLIC_CLIENT_ID") or os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    if not client_id:
        raise RuntimeError("PUBLIC_CLIENT_ID (or CLIENT_ID) must be set for delegated auth (device code). Use the App (client) ID of a Public client app with 'Allow public client flows' enabled.")
    if not tenant_id:
        raise RuntimeError("TENANT_ID must be set for delegated auth (device code)")
    if msal is None:
        raise RuntimeError("msal is required. Install with: pip install msal")

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    env_scopes = os.getenv("DELEGATED_SCOPES")
    if env_scopes:
        scopes = [s for s in env_scopes.replace(",", " ").split() if s]
    else:
        scopes = scopes or ["Files.Read", "offline_access"]

    # Setup token cache
    token_cache, cache_file = _get_token_cache(cache_path)
    app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=token_cache)

    # Try silent token first
    try:
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])
            if isinstance(result, dict) and "access_token" in result:
                _save_token_cache(token_cache, cache_file)
                return result["access_token"]
    except Exception:
        pass

    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise RuntimeError(f"Failed to initiate device flow: {flow}")
    print(flow["message"])  # Display instructions to the user
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise RuntimeError(f"Failed to acquire delegated token: {result}")
    _save_token_cache(token_cache, cache_file)
    return result["access_token"]


def _acquire_delegated_token_via_ropc(username: str, password: str, scopes: Optional[List[str]] = None, cache_path: Optional[str] = None) -> str:
    """
    Acquire token using ROPC (username/password). Requires tenant to allow it and account without MFA.
    """
    client_id = os.getenv("PUBLIC_CLIENT_ID") or os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    if not client_id:
        raise RuntimeError("PUBLIC_CLIENT_ID (or CLIENT_ID) must be set for delegated auth (ROPC). Use the App (client) ID of a Public client app with 'Allow public client flows' enabled.")
    if not tenant_id:
        raise RuntimeError("TENANT_ID must be set for delegated auth (ROPC)")
    if msal is None:
        raise RuntimeError("msal is required. Install with: pip install msal")

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    env_scopes = os.getenv("DELEGATED_SCOPES")
    if env_scopes:
        scopes = [s for s in env_scopes.replace(",", " ").split() if s]
    else:
        scopes = scopes or ["Files.Read", "offline_access"]

    token_cache, cache_file = _get_token_cache(cache_path)
    app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=token_cache)

    # Try silent first if cache has an account for this username
    try:
        accounts = [a for a in app.get_accounts(username=username)]
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])
            if isinstance(result, dict) and "access_token" in result:
                _save_token_cache(token_cache, cache_file)
                return result["access_token"]
    except Exception:
        pass

    result = app.acquire_token_by_username_password(username=username, password=password, scopes=scopes)
    if "access_token" not in result:
        raise RuntimeError(f"Failed to acquire delegated token via username/password: {result}")
    _save_token_cache(token_cache, cache_file)
    return result["access_token"]


def _build_headers(access_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


_TEXT_LIKE_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}
_BINARY_DOC_EXTENSIONS = {".pdf", ".doc", ".docx"}


def _infer_name_and_mime(item: Dict[str, Any]) -> Dict[str, Optional[str]]:
    remote = (item or {}).get("remoteItem") or {}
    file_info = (item.get("file") or remote.get("file") or {})
    return {
        "name": item.get("name") or remote.get("name"),
        "mime": file_info.get("mimeType"),
    }


def _resolve_drive_and_item_ids(item: Dict[str, Any]) -> Optional[Dict[str, str]]:
    # Prefer remoteItem info when present
    remote = (item or {}).get("remoteItem") or {}
    parent = (remote.get("parentReference") or item.get("parentReference") or {})
    drive_id = parent.get("driveId")
    item_id = remote.get("id") or item.get("id")
    if drive_id and item_id:
        return {"drive_id": drive_id, "item_id": item_id}
    return None


def _download_item_text(drive_id: str, item_id: str, access_token: str, *, max_bytes: int = 65536) -> Optional[str]:
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    if resp.status_code >= 400:
        return None
    content_type = resp.headers.get("Content-Type", "")
    if not (content_type.startswith("text/") or content_type in ("application/json", "application/xml")):
        # Likely binary; do not attempt to print
        return None
    # Read up to max_bytes
    data = resp.raw.read(max_bytes)
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def _download_item_bytes(drive_id: str, item_id: str, access_token: str, *, max_bytes: int = 5 * 1024 * 1024) -> Optional[bytes]:
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, stream=True, timeout=120)
    if resp.status_code >= 400:
        return None
    # Limit download size to avoid huge files
    data = resp.raw.read(max_bytes)
    return data


def _extract_text_from_docx_bytes(data: bytes) -> Optional[str]:
    try:
        import docx  # python-docx
    except ImportError:
        print("Note: python-docx not installed. Install with: pip install python-docx")
        return None
    try:
        doc = docx.Document(BytesIO(data))
        parts = []
        for p in doc.paragraphs:
            if p.text:
                parts.append(p.text)
        return "\n".join(parts)
    except Exception:
        return None


def _extract_text_from_pdf_bytes(data: bytes) -> Optional[str]:
    # Try PyPDF2 (pypdf) first
    try:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            from pypdf import PdfReader  # type: ignore
        reader = PdfReader(BytesIO(data))
        pages_text = []
        for page in getattr(reader, "pages", []):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            pages_text.append(txt)
        text = "\n".join(pages_text).strip()
        if text:
            return text
    except Exception:
        pass

    # Fallback to pdfminer.six if available
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        text = extract_text(BytesIO(data))
        return text
    except Exception:
        print("Note: No PDF text extractor available. Install with: pip install pypdf or pip install pdfminer.six")
        return None


def list_shared_with_me(
    *,
    access_token: Optional[str] = None,
    top: int = 100,
    use_device_code: bool = False,
    cache_path: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    text_files_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    List files and folders that are "Shared with me" (requires DELEGATED permissions).

    OneDrive "sharedWithMe" is NOT available with application permissions.
    Provide a delegated access token, or set use_device_code=True to sign in interactively.
    """
    # Auto-detect credentials from environment if not provided
    if not access_token and not use_device_code and not (username and password):
        env_username = os.getenv("GRAPH_USERNAME")
        env_password = os.getenv("GRAPH_PASSWORD")
        
        if env_username and env_password:
            username = env_username
            password = env_password
        elif env_username:
            # If only username is provided, use device code
            use_device_code = True
        else:
            raise RuntimeError(
                "sharedWithMe requires delegated permissions. Provide access_token, or username/password (ROPC), or set use_device_code=True"
            )

    token: str
    if access_token:
        token = access_token
    elif username and password:
        # Try ROPC first, fall back to device code if MFA is required
        try:
            token = _acquire_delegated_token_via_ropc(username=username, password=password, cache_path=cache_path)
        except RuntimeError as e:
            if "AADSTS50076" in str(e) or "multi-factor authentication" in str(e).lower():
                print("Username/password authentication failed due to MFA requirement")
                print("Falling back to device code authentication...")
                token = _acquire_delegated_token_via_device_code(cache_path=cache_path)
            else:
                raise
    else:
        token = _acquire_delegated_token_via_device_code(cache_path=cache_path)
    
    headers = _build_headers(token)

    # Define text file extensions to filter for
    text_extensions = {
        '.doc', '.docx', '.pdf', '.txt', '.md', '.rtf', 
        '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
        '.csv', '.json', '.xml', '.html', '.htm', '.log'
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/sharedWithMe?$top=50"
    
    items: List[Dict[str, Any]] = []
    while url and len(items) < top:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code >= 400:
            try:
                err_json = resp.json()
                err_msg = err_json.get("error", {}).get("message")
            except Exception:
                err_msg = resp.text
            raise RuntimeError(f"sharedWithMe failed: {resp.status_code} {err_msg}")

        data = resp.json()
        page_items = data.get("value", [])
        for it in page_items:
            # Apply text file filter if requested
            if text_files_only:
                item_name = it.get('name', '')
                file_ext = None
                
                # Check if it's a file (not folder) and get extension
                if it.get('file'):
                    file_ext = '.' + item_name.split('.')[-1].lower() if '.' in item_name else None
                
                # Skip if it's not a text file
                if not file_ext or file_ext not in text_extensions:
                    continue
            
            items.append(it)
            if len(items) >= top:
                break
        url = data.get("@odata.nextLink") if len(items) < top else None

    return items


def display_shared_items(items):
    """Display shared items in a nice format"""
    if not items:
        print("📭 No shared items found.")
        return
    
    print(f"\nSHARED ITEMS ({len(items)} items)")
    print("=" * 80)
    
    for i, item in enumerate(items, 1):
        # Extract item info
        remote = (item or {}).get("remoteItem") or {}
        name = item.get("name") or remote.get("name") or "Unknown"
        item_id = item.get("id") or remote.get("id") or "Unknown"
        is_folder = bool((item.get("folder") or remote.get("folder")) is not None)
        last_modified = item.get("lastModifiedDateTime") or remote.get("lastModifiedDateTime") or "Unknown"
        web_url = item.get("webUrl") or remote.get("webUrl") or "Unknown"
        
        # Try to get shared by information from multiple sources
        shared_by = "Unknown"
        if remote.get("createdBy", {}).get("user", {}).get("displayName"):
            shared_by = remote.get("createdBy", {}).get("user", {}).get("displayName")
        elif item.get("createdBy", {}).get("user", {}).get("displayName"):
            shared_by = item.get("createdBy", {}).get("user", {}).get("displayName")
        elif item.get("owner", {}).get("user", {}).get("displayName"):
            shared_by = item.get("owner", {}).get("user", {}).get("displayName")
        
        # Format size
        size = item.get("size") or remote.get("size") or 0
        if isinstance(size, int):
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size // 1024} KB"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size // (1024 * 1024)} MB"
            else:
                size_str = f"{size // (1024 * 1024 * 1024)} GB"
        else:
            size_str = str(size)
        
        # Determine item type
        if is_folder:
            icon = "[FOLDER]"
            item_type = "Folder"
        elif item.get("file"):
            icon = "[FILE]"
            item_type = "File"
        elif remote.get("file"):
            icon = "[FILE]"
            item_type = "Shared File"
        else:
            icon = "[FILE]"
            item_type = "Item"
        
        # Display item
        print(f"{i:2d}. {icon} {name}")
        print(f"    Type: {item_type}")
        print(f"    Size: {size_str}")
        print(f"    Shared by: {shared_by}")
        print(f"    Modified: {last_modified}")
        print(f"    URL: {web_url}")
        
        # Show drive information if available
        if item.get("drive_name"):
            print(f"    Drive: {item.get('drive_name')} ({item.get('drive_type', 'Unknown')})")
        
        # Show source information
        if item.get("source"):
            print(f"    Source: {item.get('source')}")
        
        # Show additional info for shared items
        if remote:
            print(f"    Remote ID: {remote.get('id', 'N/A')}")
            print(f"    Remote Drive: {remote.get('parentReference', {}).get('driveId', 'N/A')}")
        
        print(f"    ID: {item_id}")
        print("-" * 80)


def display_file_content(file_item, access_token: str):
    """Display the content of a selected file"""
    # Get file info
    remote = (file_item or {}).get("remoteItem") or {}
    name = file_item.get("name") or remote.get("name") or "Unknown"
    file_id = file_item.get("id") or remote.get("id")
    
    if not file_id:
        print("Cannot display content: No file ID found")
        return
    
    # Determine drive and item IDs
    drive_item_ids = _resolve_drive_and_item_ids(file_item)
    if not drive_item_ids:
        print("Cannot display content: Could not resolve drive and item IDs")
        return
    
    drive_id = drive_item_ids["drive_id"]
    item_id = drive_item_ids["item_id"]
    
    # Try to download and display text content
    text_content = _download_item_text(drive_id, item_id, access_token)
    
    if text_content:
        print(f"\nFILE CONTENT:")
        print("=" * 60)
        print(text_content)
        print("=" * 60)
    else:
        # Try to extract text from binary files
        
        # Download file bytes
        file_bytes = _download_item_bytes(drive_id, item_id, access_token)
        
        if file_bytes:
            # Try to extract text based on file extension
            file_ext = '.' + name.split('.')[-1].lower() if '.' in name else ''
            
            extracted_text = None
            
            if file_ext in ['.docx']:
                extracted_text = _extract_text_from_docx_bytes(file_bytes)
            elif file_ext in ['.pdf']:
                extracted_text = _extract_text_from_pdf_bytes(file_bytes)
            
            if extracted_text:
                print(f"\n{extracted_text}")
            else:
                print(f"Could not extract text from {file_ext} file")
                print(f"File size: {len(file_bytes)} bytes")
        else:
            print(f"Could not download file content")


def main():
    print("============================================================")
    print("ONEDRIVE SHARED ITEMS VIEWER")
    print("============================================================")
    
    # Get number of items to retrieve
    while True:
        try:
            top_input = input("Enter number of items to retrieve (1-100, default: 20): ").strip()
            if not top_input:
                top = 20
                break
            else:
                top = int(top_input)
                if 1 <= top <= 100:
                    break
                else:
                    print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Always show text files only
    text_only = True
    
    try:
        print(f"\nRetrieving up to {top} shared text files...")
        print("=" * 60)
        
        # Get shared files using automated authentication
        results = list_shared_with_me(
            top=top, 
            text_files_only=text_only,
            cache_path=".msal_token_cache.bin"
        )
        
        # Display results in simplified format
        simplified = []
        for it in results:
            # sharedWithMe often returns a DriveItem with remoteItem metadata
            remote = (it or {}).get("remoteItem") or {}
            simplified.append({
                "name": it.get("name") or remote.get("name"),
                "id": it.get("id") or remote.get("id"),
                "isFolder": bool((it.get("folder") or remote.get("folder")) is not None),
                "lastModified": it.get("lastModifiedDateTime") or remote.get("lastModifiedDateTime"),
                "webUrl": it.get("webUrl") or remote.get("webUrl"),
                "from": (remote.get("createdBy", {}) or {}).get("user", {}).get("displayName")
            })
        
        display_shared_items(results)
        
        # Get access token for file content viewing
        username = os.getenv("GRAPH_USERNAME")
        password = os.getenv("GRAPH_PASSWORD")
        
        try:
            if username and password:
                # Try ROPC first, fall back to device code if MFA is required
                try:
                    token = _acquire_delegated_token_via_ropc(username, password, cache_path=".msal_token_cache.bin")
                except RuntimeError as e:
                    if "AADSTS50076" in str(e) or "multi-factor authentication" in str(e).lower():
                        print("Username/password authentication failed due to MFA requirement")
                        print("Falling back to device code authentication...")
                        token = _acquire_delegated_token_via_device_code(cache_path=".msal_token_cache.bin")
                    else:
                        raise
            elif username:
                token = _acquire_delegated_token_via_device_code(cache_path=".msal_token_cache.bin")
            else:
                token = _acquire_delegated_token_via_device_code(cache_path=".msal_token_cache.bin")
        except Exception as e:
            print(f"Authentication failed: {e}")
            return
        
        # Add file selection and display feature
        if results:
            print("\n" + "=" * 60)
            print("FILE CONTENT VIEWER")
            print("=" * 60)
            
            while True:
                try:
                    selection = input("\nEnter file number to view content (or 'q' to quit): ").strip()
                    
                    if selection.lower() == 'q':
                        print("Goodbye!")
                        break
                    
                    file_index = int(selection) - 1
                    if 0 <= file_index < len(results):
                        selected_file = results[file_index]
                        display_file_content(selected_file, token)
                    else:
                        print(f"❌ Invalid selection. Please enter a number between 1 and {len(results)}")
                        
                except ValueError:
                    print("❌ Please enter a valid number or 'q' to quit")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


