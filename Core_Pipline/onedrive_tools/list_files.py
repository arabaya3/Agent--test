import os
from typing import Optional, List, Dict, Any
import requests

try:
    from shared.auth import get_access_token
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from shared.auth import get_access_token


def _normalize_path(path_value: Optional[str]) -> str:
    if not path_value:
        return ""
    return path_value.replace("\\", "/").strip("/")


def _build_headers() -> Dict[str, str]:
    token = get_access_token()
    if not token:
        raise RuntimeError("Failed to obtain access token. Check environment and app permissions.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }


def list_onedrive_files(
    *,
    user_id: Optional[str] = None,
    drive_id: Optional[str] = None,
    folder_path: Optional[str] = None,
    top: int = 100,
) -> List[Dict[str, Any]]:
    if not user_id and not drive_id:
        raise ValueError("Either user_id or drive_id must be provided")

    headers = _build_headers()
    normalized = _normalize_path(folder_path)

    if user_id:
        if normalized:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{normalized}:/children?$top=200"
        else:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root/children?$top=200"
    else:
        if normalized:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalized}:/children?$top=200"
        else:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children?$top=200"

    items: List[Dict[str, Any]] = []
    while url and len(items) < top:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code >= 400:
            try:
                err_json = resp.json()
                err_msg = err_json.get("error", {}).get("message")
            except Exception:
                err_msg = resp.text
            if resp.status_code == 404 and err_msg and "User not found" in err_msg:
                raise RuntimeError("User not found. Provide a valid email/UPN or object ID, or use drive ID. Ensure the user's OneDrive is provisioned.")
            raise RuntimeError(f"List request failed: {resp.status_code} {err_msg}")

        data = resp.json()
        page_items = data.get("value", [])
        for it in page_items:
            items.append(it)
            if len(items) >= top:
                break
        url = data.get("@odata.nextLink") if len(items) < top else None

    return items


def display_files(items):
    """Display files in a nice format"""
    if not items:
        print("No files found in the specified location.")
        return
    
    print(f"\n📁 FILES AND FOLDERS ({len(items)} found):")
    print("=" * 80)
    
    for i, item in enumerate(items, 1):
        name = item.get("name", "Unknown")
        item_id = item.get("id", "Unknown")
        size = item.get("size", 0)
        is_folder = bool(item.get("folder"))
        last_modified = item.get("lastModifiedDateTime", "Unknown")
        web_url = item.get("webUrl", "")
        
        # Format size
        if size == 0:
            size_str = "0 B"
        elif size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size // 1024} KB"
        elif size < 1024 * 1024 * 1024:
            size_str = f"{size // (1024 * 1024)} MB"
        else:
            size_str = f"{size // (1024 * 1024 * 1024)} GB"
        
        # Format last modified date
        if last_modified != "Unknown":
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                last_modified = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        folder_icon = "📁" if is_folder else "📄"
        print(f"{i:2d}. {folder_icon} {name}")
        print(f"    🆔 ID: {item_id}")
        print(f"    📏 Size: {size_str}")
        print(f"    📅 Modified: {last_modified}")
        if web_url:
            print(f"    🔗 URL: {web_url}")
        print("-" * 80)

def main():
    print("============================================================")
    print("📁 ONEDRIVE FILE LISTER")
    print("============================================================")
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot list OneDrive files.")
        return
    
    print(f"Using user: {target_user}")
    
    # Get folder path
    folder_path = input("Enter folder path (leave blank for root): ").strip()
    
    # Get number of items
    while True:
        try:
            top_input = input("How many items to list? (1-1000, default: 100): ").strip()
            if not top_input:
                top = 100
                break
            else:
                top = int(top_input)
                if 1 <= top <= 1000:
                    break
                else:
                    print("Please enter a number between 1 and 1000.")
        except ValueError:
            print("Please enter a valid number.")
    
    try:
        print(f"\n🔍 Listing files in: {folder_path if folder_path else 'root'}")
        print("=" * 60)
        
        items = list_onedrive_files(user_id=target_user, folder_path=folder_path, top=top)
        display_files(items)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


