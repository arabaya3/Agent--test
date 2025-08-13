import os
import json
import re
from typing import Optional, Dict, Any, List

try:
    import aixplain as ax
    HAS_AIXPLAIN = True
except Exception:
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


SYSTEM_DECISION_PROMPT = (
    "You are a strict router. Decide which enterprise tool to use and return JSON only. "
    "tools: ['email_by_id','email_by_sender_date','email_by_date_range','email_by_subject_date_range',"
    "'calendar_by_date','calendar_by_organizer_date','calendar_by_date_range','calendar_by_subject_date_range',"
    "'meeting_by_id','meeting_by_title','meeting_transcript','meeting_audience','meeting_attendance',"
    "'onedrive_list','onedrive_download','onedrive_upload']. "
    "Return fields needed by that tool and null for unknowns."
)


def _run_aixplain(query: str) -> Optional[Dict[str, Any]]:
    if not HAS_AIXPLAIN:
        return None
    try:
        target_id = os.getenv("AIXPLAIN_MODEL_ID") or os.getenv("AIXPLAIN_CORE_PIPELINE_API")
        if not target_id:
            return None
        model = ax.Model.find(id=target_id)
        if not model:
            return None
        prompt = f"System: {SYSTEM_DECISION_PROMPT}\nUser: {query}\nAssistant:"
        out = model.run(input=prompt)
        text = out.get("output", "") if isinstance(out, dict) else str(out)
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception:
        return None
    return None


def _parse_dates(query: str) -> List[str]:
    # very basic YYYY-MM-DD detection
    return re.findall(r"\d{4}-\d{2}-\d{2}", query)


def _decide_with_rules(query: str) -> Dict[str, Any]:
    q = query.lower()
    emails = re.findall(r"[\w\.-]+@[\w\.-]+", query)
    # Don't automatically assign user_id from query - let it be handled by default_user_id
    dates = _parse_dates(query)
    ids = re.findall(r"[A-Za-z0-9-]{10,}", query)  # rough for message/meeting ids
    # quoted subject or folder/path
    quoted = re.findall(r"['\"]([^'\"]+)['\"]", query)

    # Onedrive first if 'file' or 'onedrive' mentioned
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
        # default list
        return {
            "tool": "onedrive_list",
            "folder_path": (quoted[0] if quoted else None),
            "top": 50,
        }

    # Meeting explicit features
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

    # Calendar
    if any(k in q for k in ["calendar", "meetings", "meeting schedule"]):
        if "organizer" in q and dates:
            return {"tool": "calendar_by_organizer_date", "organizer": (emails[1] if len(emails) > 1 else emails[0] if emails else quoted[0] if quoted else None), "date": dates[0]}
        if len(dates) >= 2:
            return {"tool": "calendar_by_date_range", "start_date": dates[0], "end_date": dates[1]}
        if ("subject" in q or "title" in q) and dates:
            return {"tool": "calendar_by_subject_date_range", "subject": (quoted[0] if quoted else None), "start_date": dates[0], "end_date": dates[1] if len(dates) > 1 else dates[0]}
        if dates:
            return {"tool": "calendar_by_date", "date": dates[0]}

    # Email
    if "email" in q or "emails" in q or "inbox" in q:
        if "id" in q and ids:
            return {"tool": "email_by_id", "email_ids": ids}
        # Check for date range first (more specific)
        if len(dates) >= 2:
            return {"tool": "email_by_date_range", "start_date": dates[0], "end_date": dates[1]}
        # Check for sender query (must have email address and single date)
        if "from" in q and dates and len(dates) == 1 and emails and any("@" in email for email in emails):
            # find sender from email list or quoted
            sender = (emails[1] if len(emails) > 1 else emails[0] if emails else quoted[0] if quoted else None)
            return {"tool": "email_by_sender_date", "sender": sender, "date": dates[0]}
        if "subject" in q and len(dates) >= 1:
            subject = quoted[0] if quoted else None
            start_date = dates[0]
            end_date = dates[1] if len(dates) > 1 else dates[0]
            return {"tool": "email_by_subject_date_range", "subject": subject, "start_date": start_date, "end_date": end_date}
        # Single date fallback
        if dates:
            return {"tool": "email_by_date_range", "start_date": dates[0], "end_date": dates[0]}

    # fallback
    return {"tool": "onedrive_list", "folder_path": None, "top": 50}


def handle_query(query: str, default_user_id: Optional[str] = None) -> Dict[str, Any]:
    decision = _run_aixplain(query) or _decide_with_rules(query)
    tool = decision.get("tool")
    user_id = decision.get("user_id") or default_user_id

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


