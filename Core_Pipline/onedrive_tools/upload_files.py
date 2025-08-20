import math
import os
from typing import Optional, Dict, Any
import requests

try:
    from shared.auth import get_access_token
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from shared.auth import get_access_token


def _build_headers() -> Dict[str, str]:
    access_token = get_access_token()
    if not access_token:
        raise RuntimeError("Failed to obtain access token. Check CLIENT_ID, TENANT_ID, CLIENT_SECRET.")
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }


def _normalize_path(path_value: str) -> str:
                                     
    return (path_value or "").replace("\\", "/").lstrip("/")


def _resolve_simple_upload_url(user_id: Optional[str], drive_id: Optional[str], item_path: str) -> str:
    normalized_path = _normalize_path(item_path)

    if user_id:
        return f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{normalized_path}:/content"
    if drive_id:
        return f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalized_path}:/content"
    raise ValueError("Either user_id or drive_id must be provided.")


def _resolve_session_url(user_id: Optional[str], drive_id: Optional[str], item_path: str) -> str:
    normalized_path = _normalize_path(item_path)

    if user_id:
        return f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{normalized_path}:/createUploadSession"
    if drive_id:
        return f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalized_path}:/createUploadSession"
    raise ValueError("Either user_id or drive_id must be provided.")


def upload_onedrive_file(
    *,
    file_path: str,
    destination_path: str,
    user_id: Optional[str] = None,
    drive_id: Optional[str] = None,
    conflict_behavior: str = "replace",
    chunk_size_bytes: int = 5 * 1024 * 1024,
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not destination_path:
        raise ValueError("destination_path is required")
    if conflict_behavior not in {"replace", "rename", "fail"}:
        raise ValueError("conflict_behavior must be one of 'replace', 'rename', 'fail'")

    file_size = os.path.getsize(file_path)
    headers = _build_headers()

                                            
    if file_size <= 4 * 1024 * 1024:
        url = _resolve_simple_upload_url(user_id=user_id, drive_id=drive_id, item_path=destination_path)
        with open(file_path, "rb") as fp:
            resp = requests.put(url, headers=headers, data=fp, timeout=timeout_seconds)
        if resp.status_code >= 400:
            try:
                err_json = resp.json()
                err_msg = err_json.get("error", {}).get("message")
            except Exception:
                err_msg = resp.text
            if resp.status_code == 404 and err_msg and "User not found" in err_msg:
                raise RuntimeError("User not found. Provide a valid --user-id (UPN or object ID) or use --drive-id. Also ensure the user's OneDrive is provisioned.")
            raise RuntimeError(f"Simple upload failed: {resp.status_code} {err_msg}")
        return resp.json()

                                          
    session_url = _resolve_session_url(user_id=user_id, drive_id=drive_id, item_path=destination_path)
    session_body = {
        "item": {
            "@microsoft.graph.conflictBehavior": conflict_behavior
        }
    }
    create_resp = requests.post(session_url, headers=headers, json=session_body, timeout=timeout_seconds)
    if create_resp.status_code >= 400:
        try:
            err_json = create_resp.json()
            err_msg = err_json.get("error", {}).get("message")
        except Exception:
            err_msg = create_resp.text
        if create_resp.status_code == 404 and err_msg and "User not found" in err_msg:
            raise RuntimeError("User not found. Provide a valid --user-id (UPN or object ID) or use --drive-id. Also ensure the user's OneDrive is provisioned.")
        raise RuntimeError(f"Failed to create upload session: {create_resp.status_code} {err_msg}")
    upload_url = create_resp.json().get("uploadUrl")
    if not upload_url:
        raise RuntimeError("Upload session did not return an uploadUrl")

    bytes_uploaded = 0
    total_bytes = file_size
    with open(file_path, "rb") as fp:
        while bytes_uploaded < total_bytes:
            chunk = fp.read(chunk_size_bytes)
            if not chunk:
                break

            start_index = bytes_uploaded
            end_index = bytes_uploaded + len(chunk) - 1
            content_range = f"bytes {start_index}-{end_index}/{total_bytes}"

            chunk_headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": content_range
            }
            chunk_headers.update(headers)

            put_resp = requests.put(upload_url, headers=chunk_headers, data=chunk, timeout=timeout_seconds)
            if put_resp.status_code in (200, 201):
                           
                return put_resp.json()
            if put_resp.status_code not in (202,):
                raise RuntimeError(f"Chunk upload failed: {put_resp.status_code} {put_resp.text}")

                                                                  
            bytes_uploaded = end_index + 1

                                                                                    
    status_resp = requests.get(upload_url, headers=headers, timeout=timeout_seconds)
    if status_resp.status_code in (200, 201):
        return status_resp.json()
    raise RuntimeError(f"Upload session did not complete successfully: {status_resp.status_code} {status_resp.text}")

def display_upload_result(result):
    """Display upload result in a nice format"""
    print("\n📄 FILE UPLOADED SUCCESSFULLY!")
    print("=" * 60)
    print(f"🆔 ID: {result.get('id', 'Unknown')}")
    print(f"📝 Name: {result.get('name', 'Unknown')}")
    print(f"📏 Size: {result.get('size', 'Unknown')} bytes")
    print(f"🔗 Web URL: {result.get('webUrl', 'Unknown')}")
    
    # Format file size
    size = result.get('size', 0)
    if isinstance(size, int):
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size // 1024} KB"
        elif size < 1024 * 1024 * 1024:
            size_str = f"{size // (1024 * 1024)} MB"
        else:
            size_str = f"{size // (1024 * 1024 * 1024)} GB"
        print(f"📊 Formatted Size: {size_str}")
    
    print("=" * 60)

def main():
    print("============================================================")
    print("📤 ONEDRIVE FILE UPLOADER")
    print("============================================================")
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot upload to OneDrive.")
        return
    
    print(f"Using user: {target_user}")
    
    # Get local file path
    file_path = input("Enter local file path to upload: ").strip()
    if not file_path:
        print("Error: File path is required")
        return
    
    # Remove quotes if present and handle file URIs
    file_path = file_path.strip("'\"")
    
    # Handle file:/// URIs
    if file_path.startswith("file:///"):
        file_path = file_path[8:]  # Remove "file:///" prefix
    elif file_path.startswith("file://"):
        file_path = file_path[7:]  # Remove "file://" prefix
    
    # Convert forward slashes to backslashes on Windows
    if os.name == 'nt':
        file_path = file_path.replace('/', '\\')
    
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    # Format file size for display
    if file_size < 1024:
        size_str = f"{file_size} B"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size // 1024} KB"
    elif file_size < 1024 * 1024 * 1024:
        size_str = f"{file_size // (1024 * 1024)} MB"
    else:
        size_str = f"{file_size // (1024 * 1024 * 1024)} GB"
    
    print(f"📄 File: {file_name}")
    print(f"📊 Size: {size_str}")
    
    # Get destination path
    dest_path = input(f"Enter OneDrive destination path (e.g., Documents/{file_name}): ").strip()
    if not dest_path:
        dest_path = f"Documents/{file_name}"
        print(f"Using default: {dest_path}")
    
    # Remove quotes if present
    dest_path = dest_path.strip("'\"")
    
    # If destination doesn't include a filename, add the original filename
    if not dest_path.endswith('/') and '.' not in os.path.basename(dest_path):
        # Looks like a folder path, add the filename
        dest_path = f"{dest_path}/{file_name}"
        print(f"Added filename to path: {dest_path}")
    
    # Get conflict behavior
    print("\nConflict behavior options:")
    print("1. replace - Replace existing file")
    print("2. rename - Rename if file exists")
    print("3. fail - Fail if file exists")
    
    while True:
        conflict_choice = input("Choose conflict behavior (1-3, default: 1): ").strip()
        if not conflict_choice or conflict_choice == "1":
            conflict_behavior = "replace"
            break
        elif conflict_choice == "2":
            conflict_behavior = "rename"
            break
        elif conflict_choice == "3":
            conflict_behavior = "fail"
            break
        else:
            print("Please enter 1, 2, or 3")
    
    # Get timeout
    while True:
        try:
            timeout_input = input("Enter timeout in seconds (30-600, default: 120): ").strip()
            if not timeout_input:
                timeout = 120
                break
            else:
                timeout = int(timeout_input)
                if 30 <= timeout <= 600:
                    break
                else:
                    print("Please enter a number between 30 and 600.")
        except ValueError:
            print("Please enter a valid number.")
    
    try:
        print(f"\n📤 Uploading file to: {dest_path}")
        print(f"🔄 Conflict behavior: {conflict_behavior}")
        print("=" * 60)
        
        result = upload_onedrive_file(
            file_path=file_path,
            destination_path=dest_path,
            user_id=target_user,
            conflict_behavior=conflict_behavior,
            timeout_seconds=timeout,
        )
        
        display_upload_result(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


