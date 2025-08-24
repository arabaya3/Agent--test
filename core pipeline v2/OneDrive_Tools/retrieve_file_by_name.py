import os
import json
import base64
import io
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


def retrieve_file_by_name(file_name: str = "") -> str:
    auth = OneDriveAuth()
    result = []
    result.append("=== OneDrive File Retrieval ===\n")

    if not file_name:
        return "ERROR: File name is required"

    try:
        headers = auth.get_headers()
        result.append("Authentication successful\n")

        api_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/drive/root/children"
        target_file = None
        file_id = None
        
        file_name_lower = file_name.lower()
        file_name_without_ext = os.path.splitext(file_name_lower)[0]
        
        supported_extensions = ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']
        
        while api_url:
            response = requests.get(api_url, headers=headers, timeout=API_TIMEOUT)

            if response.status_code >= 400:
                try:
                    err = response.json()
                    err_msg = err.get('error', {}).get('message', response.text)
                    return f"ERROR: API request failed - {response.status_code}: {err_msg}"
                except:
                    return f"ERROR: Request failed - {response.status_code}: {response.text}"

            data_response = response.json()
            items = data_response.get('value', [])
            for item in items:
                item_name = item.get('name', '').lower()
                item_name_without_ext = os.path.splitext(item_name)[0]
                
                if not bool(item.get('folder')):
                    if (item_name == file_name_lower or 
                        item_name_without_ext == file_name_without_ext or
                        (file_name_without_ext and item_name.startswith(file_name_without_ext + '.'))):
                        target_file = item
                        file_id = item.get('id')
                        break
            if target_file:
                break
            api_url = data_response.get('@odata.nextLink')

        if not target_file:
            return f"ERROR: File '{file_name}' not found"

        metadata_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/drive/items/{file_id}"
        metadata_response = requests.get(metadata_url, headers=headers, timeout=API_TIMEOUT)

        if metadata_response.status_code >= 400:
            try:
                err = metadata_response.json()
                err_msg = err.get('error', {}).get('message', metadata_response.text)
                if metadata_response.status_code == 404:
                    return f"ERROR: File '{file_name}' not found"
                return f"ERROR: API request failed - {metadata_response.status_code}: {err_msg}"
            except:
                return f"ERROR: Request failed - {metadata_response.status_code}: {metadata_response.text}"

        metadata = metadata_response.json()
        name = metadata.get('name', 'Unknown')
        size = metadata.get('size', 0)
        last_modified = metadata.get('lastModifiedDateTime', 'Unknown')
        web_url = metadata.get('webUrl', '')
        is_folder = bool(metadata.get('folder'))

        if is_folder:
            return f"ERROR: Item '{name}' is a folder, not a file"

        size_str = format_file_size(size)
        last_modified = format_datetime(last_modified)

        result.append("File Details:")
        result.append(f"Name: {name}")
        result.append(f"ID: {file_id}")
        result.append(f"Size: {size_str}")
        result.append(f"Modified: {last_modified}")
        if web_url:
            result.append(f"URL: {web_url}")
        result.append("=" * 80)

        download_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/drive/items/{file_id}/content"
        download_response = requests.get(download_url, headers=headers, timeout=API_TIMEOUT * 2)

        if download_response.status_code >= 400:
            try:
                err = download_response.json()
                err_msg = err.get('error', {}).get('message', download_response.text)
                return f"ERROR: Download failed - {download_response.status_code}: {err_msg}"
            except:
                return f"ERROR: Download failed - {download_response.status_code}: {download_response.text}"

        content = download_response.content
        file_extension = os.path.splitext(name.lower())[1]

        if size > MAX_FILE_SIZE_DISPLAY:
            result.append(f"File too large ({size_str}) - content not displayed")
        else:
            readable_content = None
            if file_extension == '.pdf':
                try:
                    import pypdf
                    pdf_file = io.BytesIO(content)
                    pdf_reader = pypdf.PdfReader(pdf_file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() or ""
                    readable_content = text_content.strip()
                    result.append("File Content (PDF Text Extracted):")
                except Exception as e:
                    result.append(f"PDF text extraction failed: {str(e)}")

            elif file_extension in ['.docx', '.doc']:
                try:
                    from docx import Document
                    doc_file = io.BytesIO(content)
                    doc = Document(doc_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                    readable_content = text_content.strip()
                    result.append("File Content (Word Document Text Extracted):")
                except Exception as e:
                    result.append(f"Word document text extraction failed: {str(e)}")

            elif file_extension in SUPPORTED_TEXT_EXTENSIONS:
                try:
                    text_content = content.decode('utf-8')
                    readable_content = text_content
                    result.append("File Content (Text):")
                except UnicodeDecodeError:
                    result.append("Text file encoding not supported")

            if readable_content:
                result.append("-" * 40)
                if len(readable_content) > MAX_CONTENT_LENGTH:
                    result.append(readable_content[:MAX_CONTENT_LENGTH] + "\n... [CONTENT TRUNCATED]")
                else:
                    result.append(readable_content)
            else:
                try:
                    text_content = content.decode('utf-8')
                    result.append("File Content (Text):")
                    result.append("-" * 40)
                    result.append(text_content)
                except UnicodeDecodeError:
                    base64_content = base64.b64encode(content).decode('utf-8')
                    if len(base64_content) > 1000:
                        result.append("Binary file - showing Base64 preview:")
                        result.append("-" * 40)
                        result.append(base64_content[:1000] + "... [BASE64 TRUNCATED]")
                        result.append("\nTo process this file type, install appropriate libraries:")
                        if file_extension == '.pdf':
                            result.append("- For PDF: pip install PyPDF2")
                        elif file_extension in ['.docx', '.doc']:
                            result.append("- For Word docs: pip install python-docx")
                    else:
                        result.append("File Content (Base64):")
                        result.append("-" * 40)
                        result.append(base64_content)

        result.append("-" * 80)
        result.append("File retrieved successfully")

        return "\n".join(result)

    except Exception as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    file_name = input("Enter file name to retrieve (with or without extension): ")
    result = retrieve_file_by_name(file_name)
    print(result)
