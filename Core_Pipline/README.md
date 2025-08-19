# Core-Assistant-Pipeline

Tools-only API for retrieving emails, calendar events/meetings, meeting artifacts, and OneDrive files via Microsoft Graph using application permissions. Use the FastAPI server in `tools_api.py` to call the tool endpoints directly from your apps.

## Highlights

- Real-time awareness (current date/time, relative dates)
- Conversational chat with follow-ups (short-term memory)
- Name-based queries (use names instead of emails)
- Intelligent last-email detection
- Retrieval and analysis for emails, meetings, and files
- Optional AIXplain integration with rule-based fallback
- Clean console output (no emojis, no summary/context blocks)

## Prerequisites

- Python 3.10+ (3.11 recommended)
- A Microsoft Entra ID application (App Registration) with application permissions to Microsoft Graph (see below)

## Clone

```bash
git clone https://github.com/arabaya3/Core-Assistant-Pipeline.git
cd Core-Assistant-Pipeline
```

## Project Structure (simplified)

```
Core-Assistant-Pipeline/
├── tools_api.py
├── email_tools/
├── calendar_tools/
├── meeting_tools/
├── onedrive_tools/
├── shared/
├── requirements.txt
├── AIXPLAIN_SETUP.md
├── APPLICATION_PERMISSIONS_README.md
├── ENV_SETUP_INSTRUCTIONS.md
└── README.md
```

## Setup

1) Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
.\.venv\Scripts\activate.bat
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Create .env and fill:
```env
# Microsoft Graph application credentials
CLIENT_ID=your_client_id
TENANT_ID=your_tenant_id
CLIENT_SECRET=your_client_secret

# AIXplain (optional)
AIXPLAIN_API_KEY=your_aixplain_api_key
AIXPLAIN_MODEL_ID=gpt-4

# Default user (UPN) for application-permission flows
DEFAULT_USER_ID=user@domain.com

# Optional debugging and switches
DEBUG_AUTH=0        # set to 1 to print token roles/scopes when acquiring a token
USE_GRAPH_BETA=0    # set to 1 to use the beta Graph base URL for certain endpoints
```

4) Grant Microsoft Graph permissions (application) and admin consent. See APPLICATION_PERMISSIONS_README.md. Commonly required:
- Mail.Read
- Calendars.Read
- Files.Read.All (and often Sites.Read.All)
- OnlineMeetings.Read.All
- OnlineMeetingTranscript.Read.All (for transcripts)

### Azure app registration quick guide

1. Register an app in Entra ID (App registrations) and create a client secret
2. Add the application permissions above under API permissions (Microsoft Graph)
3. Click Grant admin consent
4. Put CLIENT_ID, TENANT_ID, CLIENT_SECRET into your .env
5. Optionally set DEBUG_AUTH=1, then run once to confirm the token roles printed include OnlineMeetingTranscript.Read.All and OnlineMeetings.Read.All

## Run (Tools API)

Start the FastAPI server:
```bash
uvicorn tools_api:app --host 0.0.0.0 --port 8000
```

Health check:
```bash
curl http://localhost:8000/health
```

## Endpoints

- Email
  - POST `/email/by-id` { user_id, email_ids[] }
  - POST `/email/by-sender-date` { user_id, sender, date }
  - POST `/email/by-date-range` { user_id, start_date, end_date, sender?, limit_ids? }
  - POST `/email/by-subject-date-range` { user_id, subject, start_date, end_date, limit_ids? }

- Calendar
  - POST `/calendar/by-date` { user_id, date }
  - POST `/calendar/by-organizer-date` { user_id, organizer, date }
  - POST `/calendar/by-date-range` { user_id, start_date, end_date }
  - POST `/calendar/by-subject-date-range` { user_id, subject, start_date, end_date }

- Meetings
  - POST `/meeting/by-id` { user_id, meeting_id }
  - POST `/meeting/by-title` { user_id, title }
  - POST `/meeting/transcript` { user_id, meeting_id }
  - POST `/meeting/audience` { user_id, meeting_id }
  - POST `/meeting/attendance` { user_id, meeting_id }

- OneDrive
  - POST `/onedrive/list` { user_id?, drive_id?, folder_path?, top? }
  - POST `/onedrive/download` { item_path, user_id?, drive_id?, return_b64? }
  - POST `/onedrive/upload` { destination_path, file_b64, user_id?, drive_id?, conflict_behavior? }

## Example request (Email by subject/date range)
```bash
curl -X POST http://localhost:8000/email/by-subject-date-range \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user@domain.com",
    "subject": "Invoice",
    "start_date": "2025-08-01",
    "end_date": "2025-08-19",
    "limit_ids": 50
  }'
```

## Notes on meeting transcripts (application permissions)

- Transcript API requires OnlineMeetingTranscript.Read.All (application). OnlineMeetings.Read.All helps locate meetings.
- Always call user-scoped endpoints with app-only tokens: /users/{USER_ID}/onlineMeetings/{meetingId}/transcripts
- Provide either a Teams join URL, a numeric conference id, or a calendar event id; the app attempts to resolve these to the correct onlineMeeting id.
- Transcription must have been enabled and started during the meeting.

## Notes

- The API uses Microsoft Graph application permissions. Ensure admin consent and any Exchange Application Access Policies are configured to allow the target user(s).
- Configure credentials in `.env` as shown above.

## License

MIT License – see LICENSE
