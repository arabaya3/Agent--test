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


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="List OneDrive files in a folder")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--user-id", "--mail-id", dest="user_id", help="Target user's email/UPN or object ID")
    target.add_argument("--drive-id", help="Target drive ID")
    parser.add_argument("--folder", help="Folder path relative to root (blank for root)")
    parser.add_argument("--top", type=int, default=100, help="Max number of items to return")
    args = parser.parse_args()

    items = list_onedrive_files(user_id=args.user_id, drive_id=args.drive_id, folder_path=args.folder, top=args.top)
    simplified = [
        {
            "name": it.get("name"),
            "id": it.get("id"),
            "size": it.get("size"),
            "isFolder": bool(it.get("folder")),
            "lastModified": it.get("lastModifiedDateTime"),
            "webUrl": it.get("webUrl"),
        }
        for it in items
    ]
    print(json.dumps(simplified, indent=2))


