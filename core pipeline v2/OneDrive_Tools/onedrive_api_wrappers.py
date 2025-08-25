from typing import Dict, Any
from .list_onedrive_files import list_onedrive_files
from .list_shared_files import list_shared_files_delegated_only
from .retrieve_file_by_name import retrieve_file_by_name

def list_shared_files(top: int = 20) -> str:
    """
    Wrapper function for list_shared_files_delegated_only
    
    Args:
        top: Number of files to return (default: 20)
    
    Returns:
        Formatted string with shared files or error message
    """
    return f"""OneDrive Shared Files Access

============================================================
STATUS: Authentication Setup Required
============================================================

This endpoint requires delegated permissions with username/password authentication,
which is different from the client credentials used by other endpoints.

CURRENT ISSUE:
- The list_shared_files.py script requires delegated authentication
- Your current setup uses client credentials (application permissions)
- Delegated permissions need username/password or interactive login

SOLUTION OPTIONS:

Option 1: Use Regular OneDrive Files (Recommended)
- Endpoint: GET /api/onedrive/files
- Status: ✅ Working with current setup
- Access: Your own OneDrive files

Option 2: Configure Delegated Permissions (Advanced)
- Set up a public client application
- Configure username/password authentication
- Handle MFA challenges
- Update environment variables

Option 3: Use Microsoft Graph Explorer
- Visit: https://developer.microsoft.com/en-us/graph/graph-explorer
- Test: GET /me/drive/sharedWithMe
- Interactive authentication

WORKING ALTERNATIVES:
✅ GET /api/onedrive/files - List your OneDrive files
✅ GET /api/onedrive/file/<filename> - Get specific file content

For now, please use the regular OneDrive files endpoint: /api/onedrive/files"""

def retrieve_file_by_name_with_folder(file_name: str, folder_path: str = "") -> str:
    """
    Wrapper function for retrieve_file_by_name that includes folder path support
    
    Args:
        file_name: Name of the file to retrieve
        folder_path: Optional folder path to search in
    
    Returns:
        Formatted string with file details or error message
    """
    try:
        # For now, the original function doesn't support folder_path
        # This is a placeholder that could be enhanced later
        if folder_path:
            return f"Note: Folder path '{folder_path}' specified but not yet supported. Searching in root directory.\n\n" + retrieve_file_by_name(file_name)
        else:
            return retrieve_file_by_name(file_name)
    except Exception as e:
        return f"Error retrieving file '{file_name}': {str(e)}\nNote: Make sure the file exists in your OneDrive root directory."
