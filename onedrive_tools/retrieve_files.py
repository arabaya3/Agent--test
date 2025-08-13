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
    # Graph paths use forward slashes
    return (path_value or "").replace("\\", "/").lstrip("/")


def _resolve_download_url(user_id: Optional[str], drive_id: Optional[str], item_path: str) -> str:
    # Graph expects path segment without leading '/'
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
    """
    Download a file from OneDrive using Microsoft Graph with application permissions.

    One of user_id or drive_id must be provided.

    Args:
        item_path: The OneDrive path to the file (e.g., "Documents/report.pdf").
        user_id: Azure AD object id or UPN of the target user who owns the OneDrive.
        drive_id: Drive ID if targeting a specific drive instead of user.
        download_to: Optional local filesystem path to save the file. If provided, file is written and bytes still returned.
        timeout_seconds: Request timeout.

    Returns:
        A tuple of (file_bytes, response_headers_metadata).
    """
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

    # Include selected headers as metadata
    metadata = {
        "content_type": response.headers.get("Content-Type"),
        "content_length": response.headers.get("Content-Length"),
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }
    return content, metadata

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Download a file from OneDrive via Microsoft Graph (application permissions)")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--user-id", "--mail-id", dest="user_id", help="Target user's email/UPN or object ID owning the OneDrive")
    target.add_argument("--drive-id", help="Target drive ID")
    parser.add_argument("--path", required=True, help="OneDrive path to the file (e.g., 'Documents/report.pdf')")
    parser.add_argument("--out", help="Optional local path to save the file")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds")

    args = parser.parse_args()

    try:
        data, meta = retrieve_onedrive_file(
            item_path=args.path,
            user_id=args.user_id,
            drive_id=args.drive_id,
            download_to=args.out,
            timeout_seconds=args.timeout,
        )
        print("Download succeeded:")
        print(json.dumps(meta, indent=2))
        if not args.out:
            # If no output path is provided, indicate size only
            print(f"Downloaded bytes: {len(data)}")
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise


