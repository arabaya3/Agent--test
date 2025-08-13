import os
import json
import re
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import aixplain as ax
    HAS_AIXPLAIN = True
    # Configure AIXplain with API key
    api_key = os.getenv("AIXPLAIN_API_KEY") or os.getenv("TEAM_API_KEY")
    if api_key:
        # Set the API key for AIXplain
        os.environ["TEAM_API_KEY"] = api_key
except Exception as e:
    print(f"Warning: AIXplain not available: {e}")
    HAS_AIXPLAIN = False

from shared.auth import get_access_token
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from calendar_tools.by_date import retrieve_meetings_by_date
from calendar_tools.by_organizer_date import retrieve_meetings_by_organizer_date
from calendar_tools.by_date_range import retrieve_meetings_by_date_range
from calendar_tools.by_subject_date_range import retrieve_meetings_by_subject_date_range
from meeting_tools.by_id import retrieve_meeting_by_id
from meeting_tools.by_title import retrieve_meetings_by_title
from meeting_tools.transcript import retrieve_transcript_by_meeting_id
from meeting_tools.audience import retrieve_meeting_audience
from meeting_tools.attendance import retrieve_attendance_by_meeting_id
from onedrive_tools.list_files import list_onedrive_files
from onedrive_tools.retrieve_files import retrieve_onedrive_file
from onedrive_tools.upload_files import upload_onedrive_file


# Enhanced system prompt for AIXplain model
SYSTEM_DECISION_PROMPT = """
You are an intelligent enterprise assistant that routes user queries to the appropriate tools.

Available tools:
1. email_by_id - Retrieve emails by specific IDs
2. email_by_sender_date - Retrieve emails from a specific sender on a specific date
3. email_by_date_range - Retrieve emails within a date range
4. email_by_subject_date_range - Retrieve emails with specific subject within a date range
5. calendar_by_date - Get meetings on a specific date
6. calendar_by_organizer_date - Get meetings organized by someone on a specific date
7. calendar_by_date_range - Get meetings within a date range
8. calendar_by_subject_date_range - Get meetings with specific subject within a date range
9. meeting_by_id - Get meeting details by ID
10. meeting_by_title - Get meetings by title
11. meeting_transcript - Get meeting transcript by meeting ID
12. meeting_audience - Get meeting attendees by meeting ID
13. meeting_attendance - Get meeting attendance reports by meeting ID
14. onedrive_list - List files in OneDrive folder
15. onedrive_download - Download a file from OneDrive
16. onedrive_upload - Upload a file to OneDrive

Analyze the user query and return a JSON response with:
- tool: the appropriate tool name
- Any required parameters (sender, date, start_date, end_date, subject, email_ids, meeting_id, title, item_path, local_path, destination_path, folder_path, top, etc.)

Examples:
Query: "emails from john@example.com on 2025-08-10"
Response: {"tool": "email_by_sender_date", "sender": "john@example.com", "date": "2025-08-10"}

Query: "meetings from 2025-08-01 to 2025-08-15"
Response: {"tool": "calendar_by_date_range", "start_date": "2025-08-01", "end_date": "2025-08-15"}

Query: "list files in Documents folder"
Response: {"tool": "onedrive_list", "folder_path": "Documents", "top": 50}

Return only valid JSON, no additional text.
"""


def _run_aixplain_model(query: str) -> Optional[Dict[str, Any]]:
    """
    Use AIXplain model to intelligently route the query to the appropriate tool.
    """
    if not HAS_AIXPLAIN:
        print("AIXplain not available, falling back to rule-based logic")
        return None
    
    try:
        # Get model ID from environment
        model_id = os.getenv("AIXPLAIN_MODEL_ID")
        if not model_id:
            print("AIXPLAIN_MODEL_ID not set in environment")
            return None
        
        # Create the prompt
        prompt = f"System: {SYSTEM_DECISION_PROMPT}\n\nUser: {query}\n\nAssistant:"
        
        print(f"[AIXplain] Using model: {model_id}")
        print(f"[AIXplain] Processing query: {query}")
        
        # Initialize AIXplain client with API key
        try:
            client = ax.Aixplain(api_key=api_key)
            
            # Try to run the model using the correct API
            if hasattr(client, 'Model'):
                model = client.Model.get(id=model_id)
                if model:
                    result = model.run(data=prompt)
                    print(f"[AIXplain] Model response: {result}")
                    
                    # Extract the response
                    if hasattr(result, 'data'):
                        output = result.data
                    elif isinstance(result, dict):
                        output = result.get("data", "")
                    else:
                        output = str(result)
                    
                    print(f"[AIXplain] Raw response: {output}")
                    
                    # Parse the JSON response
                    try:
                        decision = json.loads(output)
                        print(f"[AIXplain] Parsed decision: {decision}")
                        return decision
                    except json.JSONDecodeError as e:
                        print(f"[AIXplain] JSON parsing error: {e}")
                        return None
                else:
                    print(f"Model with ID {model_id} not found")
                    return None
            else:
                print("[AIXplain] No Model found in client")
                return None
                
        except Exception as e:
            print(f"[AIXplain] API error: {e}")
            return None
                
    except Exception as e:
        print(f"[AIXplain] Error: {e}")
        return None


def _parse_dates(query: str) -> List[str]:
    """Extract dates in YYYY-MM-DD format from query."""
    return re.findall(r"\d{4}-\d{2}-\d{2}", query)


def _decide_with_rules(query: str) -> Dict[str, Any]:
    """
    Fallback rule-based decision logic when AIXplain is not available.
    """
    q = query.lower()
    emails = re.findall(r"[\w\.-]+@[\w\.-]+", query)
    dates = _parse_dates(query)
    ids = re.findall(r"[A-Za-z0-9-]{10,}", query)  # rough for message/meeting ids
    quoted = re.findall(r"['\"]([^'\"]+)['\"]", query)

    # OneDrive operations
    if any(k in q for k in ["onedrive", "file", "files", "folder", "upload", "download", "list files"]):
        if any(k in q for k in ["upload", "send"]):
            return {
                "tool": "onedrive_upload",
                "destination_path": (quoted[1] if len(quoted) >= 2 else None),
                "local_path": (quoted[0] if quoted else None),
            }
        if any(k in q for k in ["download", "get file", "retrieve file"]):
            return {
                "tool": "onedrive_download",
                "item_path": (quoted[0] if quoted else None),
                "local_path": (quoted[1] if len(quoted) >= 2 else None),
            }
        return {
            "tool": "onedrive_list",
            "folder_path": (quoted[0] if quoted else None),
            "top": 50,
        }

    # Meeting operations
    if "transcript" in q:
        return {"tool": "meeting_transcript", "meeting_id": ids[0] if ids else None}
    if "attendance" in q:
        return {"tool": "meeting_attendance", "meeting_id": ids[0] if ids else None}
    if "audience" in q or "attendees" in q:
        return {"tool": "meeting_audience", "meeting_id": ids[0] if ids else None}
    if "meeting" in q and ("id" in q or re.search(r"id\s*[:=]", q)):
        return {"tool": "meeting_by_id", "meeting_id": ids[0] if ids else None}
    if "meeting" in q and ("title" in q or "subject" in q):
        return {"tool": "meeting_by_title", "title": (quoted[0] if quoted else None)}

    # Calendar operations
    if any(k in q for k in ["calendar", "meetings", "meeting schedule"]):
        if "organizer" in q and dates:
            return {"tool": "calendar_by_organizer_date", "organizer": (emails[1] if len(emails) > 1 else emails[0] if emails else quoted[0] if quoted else None), "date": dates[0]}
        if len(dates) >= 2:
            return {"tool": "calendar_by_date_range", "start_date": dates[0], "end_date": dates[1]}
        if ("subject" in q or "title" in q) and dates:
            return {"tool": "calendar_by_subject_date_range", "subject": (quoted[0] if quoted else None), "start_date": dates[0], "end_date": dates[1] if len(dates) > 1 else dates[0]}
        if dates:
            return {"tool": "calendar_by_date", "date": dates[0]}

    # Email operations
    if "email" in q or "emails" in q or "inbox" in q:
        if "id" in q and ids:
            return {"tool": "email_by_id", "email_ids": ids}
        if "from" in q and dates and len(dates) == 1 and emails and any("@" in email for email in emails):
            sender = (emails[1] if len(emails) > 1 else emails[0] if emails else quoted[0] if quoted else None)
            return {"tool": "email_by_sender_date", "sender": sender, "date": dates[0]}
        if "subject" in q and len(dates) >= 1:
            subject = quoted[0] if quoted else None
            start_date = dates[0]
            end_date = dates[1] if len(dates) > 1 else dates[0]
            return {"tool": "email_by_subject_date_range", "subject": subject, "start_date": start_date, "end_date": end_date}
        if len(dates) >= 2:
            return {"tool": "email_by_date_range", "start_date": dates[0], "end_date": dates[1]}
        if dates:
            return {"tool": "email_by_date_range", "start_date": dates[0], "end_date": dates[0]}

    # Default fallback
    return {"tool": "onedrive_list", "folder_path": None, "top": 50}


def handle_query(query: str, default_user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Main query handler that uses AIXplain model for intelligent routing.
    Falls back to rule-based logic if AIXplain is not available.
    """
    print(f"[Agent] Processing query: {query}")
    
    # Try AIXplain model first
    decision = _run_aixplain_model(query)
    
    # Fall back to rule-based logic if AIXplain fails
    if not decision:
        print("[Agent] Using fallback rule-based logic")
        decision = _decide_with_rules(query)
    
    tool = decision.get("tool")
    user_id = decision.get("user_id") or default_user_id
    
    print(f"[Agent] Selected tool: {tool}")
    print(f"[Agent] Using user_id: {user_id}")

    # Ensure access token and headers only when needed for email calls
    headers = None
    if tool and tool.startswith("email_"):
        token = get_access_token()
        if not token:
            raise RuntimeError("Failed to acquire access token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Ensure email ids cache exists
        fetch_last_email_ids(headers, limit=100, user_id=user_id)
    
    # Execute the selected tool
    if tool == "email_by_id":
        email_ids: List[str] = decision.get("email_ids") or []
        emails = retrieve_emails_by_ids(email_ids, headers, user_id)
        return {"tool": tool, "count": len(emails)}
    if tool == "email_by_sender_date":
        emails = retrieve_emails_by_sender_date(decision.get("sender"), decision.get("date"), headers, user_id)
        return {"tool": tool, "count": len(emails)}
    if tool == "email_by_date_range":
        emails = retrieve_emails_by_date_range(decision.get("start_date"), decision.get("end_date"), headers, get_cached_email_ids(limit=100), user_id)
        return {"tool": tool, "count": len(emails)}
    if tool == "email_by_subject_date_range":
        emails = retrieve_emails_by_subject_date_range(decision.get("subject"), decision.get("start_date"), decision.get("end_date"), headers, get_cached_email_ids(limit=100), user_id)
        return {"tool": tool, "count": len(emails)}

    if tool == "calendar_by_date":
        meetings = retrieve_meetings_by_date(decision.get("date"), user_id)
        return {"tool": tool, "count": len(meetings)}
    if tool == "calendar_by_organizer_date":
        meetings = retrieve_meetings_by_organizer_date(decision.get("organizer"), decision.get("date"), user_id)
        return {"tool": tool, "count": len(meetings)}
    if tool == "calendar_by_date_range":
        meetings = retrieve_meetings_by_date_range(decision.get("start_date"), decision.get("end_date"), user_id)
        return {"tool": tool, "count": len(meetings)}
    if tool == "calendar_by_subject_date_range":
        meetings = retrieve_meetings_by_subject_date_range(decision.get("subject"), decision.get("start_date"), decision.get("end_date"), user_id)
        return {"tool": tool, "count": len(meetings)}

    if tool == "meeting_by_id":
        meeting = retrieve_meeting_by_id(decision.get("meeting_id"), user_id)
        return {"tool": tool, "found": bool(meeting)}
    if tool == "meeting_by_title":
        meetings = retrieve_meetings_by_title(decision.get("title"), user_id)
        return {"tool": tool, "count": len(meetings)}
    if tool == "meeting_transcript":
        transcript = retrieve_transcript_by_meeting_id(decision.get("meeting_id"), user_id)
        return {"tool": tool, "hasTranscript": bool(transcript)}
    if tool == "meeting_audience":
        attendees = retrieve_meeting_audience(decision.get("meeting_id"), user_id)
        return {"tool": tool, "count": len(attendees) if attendees else 0}
    if tool == "meeting_attendance":
        reports = retrieve_attendance_by_meeting_id(decision.get("meeting_id"), user_id)
        return {"tool": tool, "hasReports": bool(reports)}

    if tool == "onedrive_list":
        items = list_onedrive_files(user_id=user_id, folder_path=decision.get("folder_path"), top=int(decision.get("top", 50)))
        return {"tool": tool, "count": len(items)}
    if tool == "onedrive_download":
        item_path = decision.get("item_path")
        local_path = decision.get("local_path") or (os.path.join(".", os.path.basename(item_path)) if item_path else None)
        if not item_path:
            raise ValueError("item_path is required to download")
        _, meta = retrieve_onedrive_file(item_path=item_path, user_id=user_id, download_to=local_path)
        return {"tool": tool, "savedTo": local_path, "contentType": meta.get("content_type")}
    if tool == "onedrive_upload":
        local_path = decision.get("local_path")
        destination_path = decision.get("destination_path")
        if not local_path or not destination_path:
            raise ValueError("Upload requires local_path and destination_path")
        item = upload_onedrive_file(file_path=local_path, destination_path=destination_path, user_id=user_id)
        return {"tool": tool, "name": item.get("name"), "size": item.get("size")}

    raise ValueError(f"Unknown tool decision: {tool}")


def test_aixplain_connection():
    """Test AIXplain connection and model availability."""
    if not HAS_AIXPLAIN:
        print("❌ AIXplain not available")
        return False
    
    api_key = os.getenv("AIXPLAIN_API_KEY") or os.getenv("TEAM_API_KEY")
    if not api_key:
        print("❌ AIXPLAIN_API_KEY or TEAM_API_KEY not set")
        return False
    
    model_id = os.getenv("AIXPLAIN_MODEL_ID")
    if not model_id:
        print("❌ AIXPLAIN_MODEL_ID not set")
        return False
    
    try:
        # Test the correct AIXplain API structure
        client = ax.Aixplain()
        if hasattr(client, 'Model'):
            print("✅ AIXplain API structure: Model")
            return True
        elif hasattr(client, 'Pipeline'):
            print("✅ AIXplain API structure: Pipeline")
            return True
        else:
            print("❌ Unknown AIXplain API structure")
            print(f"Available client attributes: {[attr for attr in dir(client) if not attr.startswith('_')]}")
            return False
    except Exception as e:
        print(f"❌ AIXplain connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the agent
    print("Testing AIXplain Agent...")
    test_aixplain_connection()
    
    # Test with a sample query
    test_query = "emails from 2025-08-01 to 2025-08-13"
    print(f"\nTesting query: {test_query}")
    result = handle_query(test_query, "executive.assistant@menadevs.io")
    print(f"Result: {result}")


