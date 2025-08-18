import os
import base64
from typing import List, Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from shared.auth import get_access_token

# Emails
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids

# Calendar
from calendar_tools.by_date import retrieve_meetings_by_date
from calendar_tools.by_organizer_date import retrieve_meetings_by_organizer_date
from calendar_tools.by_date_range import retrieve_meetings_by_date_range
from calendar_tools.by_subject_date_range import retrieve_meetings_by_subject_date_range

# Meetings
from meeting_tools.by_id import retrieve_meeting_by_id
from meeting_tools.by_title import retrieve_meetings_by_title
from meeting_tools.transcript import retrieve_transcript_by_meeting_id
from meeting_tools.audience import retrieve_meeting_audience
from meeting_tools.attendance import retrieve_attendance_by_meeting_id

# OneDrive
from onedrive_tools.list_files import list_onedrive_files
from onedrive_tools.retrieve_files import retrieve_onedrive_file
from onedrive_tools.upload_files import upload_onedrive_file


app = FastAPI(title="Core Assistant Tools API", version="1.0.0")


def _auth_headers() -> Dict[str, str]:
    token = get_access_token()
    if not token:
        raise RuntimeError("Failed to acquire access token")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "tools_api"
    version: str = "1.0.0"


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


# =========================
# Email tools
# =========================

class EmailByIdsRequest(BaseModel):
    user_id: str = Field(..., description="Target user's UPN/email or object ID")
    email_ids: List[str] = Field(..., min_items=1)


@app.post("/email/by-id")
def email_by_id(req: EmailByIdsRequest) -> Dict[str, Any]:
    headers = _auth_headers()
    data = retrieve_emails_by_ids(req.email_ids, headers, req.user_id)
    return {"ok": True, "data": data or []}


class EmailBySenderDateRequest(BaseModel):
    user_id: str
    sender: str
    date: str


@app.post("/email/by-sender-date")
def email_by_sender_date(req: EmailBySenderDateRequest) -> Dict[str, Any]:
    headers = _auth_headers()
    # Warm up shared cache for efficiency
    fetch_last_email_ids(headers, limit=100, user_id=req.user_id)
    data = retrieve_emails_by_sender_date(req.sender, req.date, headers, req.user_id)
    return {"ok": True, "data": data or []}


class EmailByDateRangeRequest(BaseModel):
    user_id: str
    start_date: str
    end_date: str
    sender: Optional[str] = None
    limit_ids: int = 100


@app.post("/email/by-date-range")
def email_by_date_range(req: EmailByDateRangeRequest) -> Dict[str, Any]:
    headers = _auth_headers()
    fetch_last_email_ids(headers, limit=min(max(1, int(req.limit_ids)), 100), user_id=req.user_id)
    ids = get_cached_email_ids(limit=req.limit_ids)
    data = retrieve_emails_by_date_range(req.start_date, req.end_date, headers, ids, req.user_id)
    if req.sender:
        sender_lower = req.sender.lower()
        data = [m for m in (data or []) if m.get("from", "").lower() == sender_lower]
    return {"ok": True, "data": data or []}


class EmailBySubjectDateRangeRequest(BaseModel):
    user_id: str
    subject: str
    start_date: str
    end_date: str
    limit_ids: int = 100


@app.post("/email/by-subject-date-range")
def email_by_subject_date_range(req: EmailBySubjectDateRangeRequest) -> Dict[str, Any]:
    headers = _auth_headers()
    fetch_last_email_ids(headers, limit=min(max(1, int(req.limit_ids)), 100), user_id=req.user_id)
    ids = get_cached_email_ids(limit=req.limit_ids)
    data = retrieve_emails_by_subject_date_range(req.subject, req.start_date, req.end_date, headers, ids, req.user_id)
    return {"ok": True, "data": data or []}


# =========================
# Calendar tools
# =========================

class CalendarByDateRequest(BaseModel):
    user_id: str
    date: str


@app.post("/calendar/by-date")
def calendar_by_date(req: CalendarByDateRequest) -> Dict[str, Any]:
    data = retrieve_meetings_by_date(req.date, req.user_id)
    return {"ok": True, "data": data or []}


class CalendarByOrganizerDateRequest(BaseModel):
    user_id: str
    organizer: str
    date: str


@app.post("/calendar/by-organizer-date")
def calendar_by_organizer_date(req: CalendarByOrganizerDateRequest) -> Dict[str, Any]:
    data = retrieve_meetings_by_organizer_date(req.organizer, req.date, req.user_id)
    return {"ok": True, "data": data or []}


class CalendarByDateRangeRequest(BaseModel):
    user_id: str
    start_date: str
    end_date: str


@app.post("/calendar/by-date-range")
def calendar_by_date_range(req: CalendarByDateRangeRequest) -> Dict[str, Any]:
    data = retrieve_meetings_by_date_range(req.start_date, req.end_date, req.user_id)
    return {"ok": True, "data": data or []}


class CalendarBySubjectDateRangeRequest(BaseModel):
    user_id: str
    subject: str
    start_date: str
    end_date: str


@app.post("/calendar/by-subject-date-range")
def calendar_by_subject_date_range(req: CalendarBySubjectDateRangeRequest) -> Dict[str, Any]:
    data = retrieve_meetings_by_subject_date_range(req.subject, req.start_date, req.end_date, req.user_id)
    return {"ok": True, "data": data or []}


# =========================
# Meeting tools
# =========================

class MeetingByIdRequest(BaseModel):
    user_id: str
    meeting_id: str


@app.post("/meeting/by-id")
def meeting_by_id(req: MeetingByIdRequest) -> Dict[str, Any]:
    data = retrieve_meeting_by_id(req.meeting_id, req.user_id)
    return {"ok": True, "data": data}


class MeetingByTitleRequest(BaseModel):
    user_id: str
    title: str


@app.post("/meeting/by-title")
def meeting_by_title(req: MeetingByTitleRequest) -> Dict[str, Any]:
    data = retrieve_meetings_by_title(req.title, req.user_id)
    return {"ok": True, "data": data or []}


class MeetingTranscriptRequest(BaseModel):
    user_id: str
    meeting_id: str


@app.post("/meeting/transcript")
def meeting_transcript(req: MeetingTranscriptRequest) -> Dict[str, Any]:
    text = retrieve_transcript_by_meeting_id(req.meeting_id, req.user_id)
    return {"ok": True, "data": text or ""}


class MeetingAudienceRequest(BaseModel):
    user_id: str
    meeting_id: str


@app.post("/meeting/audience")
def meeting_audience(req: MeetingAudienceRequest) -> Dict[str, Any]:
    data = retrieve_meeting_audience(req.meeting_id, req.user_id)
    return {"ok": True, "data": data or []}


class MeetingAttendanceRequest(BaseModel):
    user_id: str
    meeting_id: str


@app.post("/meeting/attendance")
def meeting_attendance(req: MeetingAttendanceRequest) -> Dict[str, Any]:
    data = retrieve_attendance_by_meeting_id(req.meeting_id, req.user_id)
    return {"ok": True, "data": data}


# =========================
# OneDrive tools
# =========================

class OneDriveListRequest(BaseModel):
    user_id: Optional[str] = None
    drive_id: Optional[str] = None
    folder_path: Optional[str] = None
    top: int = 100


@app.post("/onedrive/list")
def onedrive_list(req: OneDriveListRequest) -> Dict[str, Any]:
    items = list_onedrive_files(user_id=req.user_id, drive_id=req.drive_id, folder_path=req.folder_path, top=req.top)
    return {"ok": True, "data": items}


class OneDriveDownloadRequest(BaseModel):
    item_path: str
    user_id: Optional[str] = None
    drive_id: Optional[str] = None
    return_b64: bool = True


@app.post("/onedrive/download")
def onedrive_download(req: OneDriveDownloadRequest) -> Dict[str, Any]:
    content_bytes, meta = retrieve_onedrive_file(item_path=req.item_path, user_id=req.user_id, drive_id=req.drive_id)
    payload: Dict[str, Any] = {"metadata": meta}
    if req.return_b64:
        payload["content_b64"] = base64.b64encode(content_bytes).decode("utf-8")
    else:
        payload["bytes"] = len(content_bytes)
    return {"ok": True, "data": payload}


class OneDriveUploadRequest(BaseModel):
    destination_path: str
    file_b64: str
    user_id: Optional[str] = None
    drive_id: Optional[str] = None
    conflict_behavior: str = "replace"


@app.post("/onedrive/upload")
def onedrive_upload(req: OneDriveUploadRequest) -> Dict[str, Any]:
    tmp_dir = ".tmp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    filename = os.path.basename(req.destination_path) or "upload.bin"
    tmp_path = os.path.join(tmp_dir, filename)
    with open(tmp_path, "wb") as fp:
        fp.write(base64.b64decode(req.file_b64))
    try:
        result = upload_onedrive_file(
            file_path=tmp_path,
            destination_path=req.destination_path,
            user_id=req.user_id,
            drive_id=req.drive_id,
            conflict_behavior=req.conflict_behavior,
        )
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return {"ok": True, "data": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tools_api:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)



