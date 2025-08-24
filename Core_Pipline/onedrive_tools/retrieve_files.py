import os
from typing import Optional, Tuple, Dict, Any
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
    """Normalize path by removing quotes, converting backslashes, and removing leading/trailing slashes"""
    if not path_value:
        return ""
    # Remove quotes and normalize slashes
    normalized = path_value.strip("'\"`").replace("\\", "/")
    # Remove leading and trailing slashes
    return normalized.strip("/")


def _resolve_download_url(user_id: Optional[str], drive_id: Optional[str], item_path: str) -> str:
                                                    
    normalized_path = _normalize_path(item_path)

    if user_id:
        return f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{normalized_path}:/content"
    if drive_id:
        return f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalized_path}:/content"
    raise ValueError("Either user_id or drive_id must be provided.")


def retrieve_onedrive_file(
    *,
    item_path: str,
    user_id: Optional[str] = None,
    drive_id: Optional[str] = None,
    download_to: Optional[str] = None,
    timeout_seconds: int = 60,
) -> Tuple[bytes, Dict[str, Any]]:
    if not item_path:
        raise ValueError("item_path is required")

    url = _resolve_download_url(user_id=user_id, drive_id=drive_id, item_path=item_path)
    headers = _build_headers()

    response = requests.get(url, headers=headers, stream=True, timeout=timeout_seconds)
    if response.status_code >= 400:
        try:
            err_json = response.json()
            err_msg = err_json.get("error", {}).get("message")
        except Exception:
            err_msg = response.text
        if response.status_code == 404 and err_msg and "User not found" in err_msg:
            raise RuntimeError("User not found. Provide a valid --user-id (UPN or object ID) or use --drive-id. Also ensure the user's OneDrive is provisioned.")
        raise RuntimeError(f"Failed to download file: {response.status_code} {err_msg}")

    content = response.content

    if download_to:
        os.makedirs(os.path.dirname(download_to) or ".", exist_ok=True)
        with open(download_to, "wb") as fp:
            fp.write(content)

                                          
    metadata = {
        "content_type": response.headers.get("Content-Type"),
        "content_length": response.headers.get("Content-Length"),
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }
    return content, metadata

def display_file_info(data, meta):
    """Display file information in a nice format"""
    print("\n📄 FILE RETRIEVED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📏 Content Length: {meta.get('content_length', 'Unknown')} bytes")
    print(f"📋 Content Type: {meta.get('content_type', 'Unknown')}")
    print(f"🆔 ETag: {meta.get('etag', 'Unknown')}")
    print(f"📅 Last Modified: {meta.get('last_modified', 'Unknown')}")
    print(f"💾 Data Size: {len(data)} bytes")
    
    # Format file size
    size = len(data)
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
    print("📄 ONEDRIVE FILE RETRIEVER")
    print("============================================================")
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot retrieve OneDrive files.")
        return
    
    print(f"Using user: {target_user}")
    
    # Get file path
    file_path = input("Enter OneDrive file path (e.g., Documents/report.pdf): ").strip()
    if not file_path:
        print("Error: File path is required")
        return
    
    # Remove quotes if present
    file_path = file_path.strip("'\"")
    
    # Get output path
    output_path = input("Enter local path to save file (leave blank to skip saving): ").strip()
    if output_path:
        # Remove quotes if present
        output_path = output_path.strip("'\"")
        
        # If output_path is a directory, create a filename from the OneDrive path
        if os.path.isdir(output_path) or not os.path.splitext(output_path)[1]:
            # Extract filename from OneDrive path
            filename = os.path.basename(file_path.strip("/"))
            if not filename:
                filename = "downloaded_file"
            output_path = os.path.join(output_path, filename)
    else:
        # Suggest a default path in the current directory
        filename = os.path.basename(file_path.strip("/"))
        if not filename:
            filename = "downloaded_file"
        output_path = os.path.join(os.getcwd(), filename)
        print(f"ℹ️  Will save to: {output_path}")
    
    # Get timeout
    while True:
        try:
            timeout_input = input("Enter timeout in seconds (1-300, default: 60): ").strip()
            if not timeout_input:
                timeout = 60
                break
            else:
                timeout = int(timeout_input)
                if 1 <= timeout <= 300:
                    break
                else:
                    print("Please enter a number between 1 and 300.")
        except ValueError:
            print("Please enter a valid number.")
    
    try:
        print(f"\n🔍 Retrieving file: {file_path}")
        print("=" * 60)
        
        data, meta = retrieve_onedrive_file(
            item_path=file_path,
            user_id=target_user,
            download_to=output_path if output_path else None,
            timeout_seconds=timeout,
        )
        
        display_file_info(data, meta)
        
        if output_path:
            print(f"✅ File saved to: {output_path}")
        else:
            print("ℹ️  File retrieved but not saved locally")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


