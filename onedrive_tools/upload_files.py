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

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Upload a file to OneDrive via Microsoft Graph (application permissions)")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--user-id", "--mail-id", dest="user_id", help="Target user's email/UPN or object ID owning the OneDrive")
    target.add_argument("--drive-id", help="Target drive ID")
    parser.add_argument("--file", required=True, help="Local path of the file to upload")
    parser.add_argument("--dest", required=True, help="Destination OneDrive path including file name (e.g., 'Documents/report.pdf')")
    parser.add_argument("--conflict", default="replace", choices=["replace", "rename", "fail"], help="Conflict behavior when the file exists")
    parser.add_argument("--chunk-size", type=int, default=5 * 1024 * 1024, help="Chunk size in bytes for large uploads (default 5MB)")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds per request")

    args = parser.parse_args()

    try:
        result = upload_onedrive_file(
            file_path=args.file,
            destination_path=args.dest,
            user_id=args.user_id,
            drive_id=args.drive_id,
            conflict_behavior=args.conflict,
            chunk_size_bytes=args.chunk_size,
            timeout_seconds=args.timeout,
        )
                                                                     
        summary = {
            "id": result.get("id"),
            "name": result.get("name"),
            "size": result.get("size"),
            "webUrl": result.get("webUrl"),
        }
        print("Upload succeeded:")
        print(json.dumps(summary, indent=2))
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise


