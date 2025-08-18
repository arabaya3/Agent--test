# Core-Assistant-Pipeline

An intelligent executive assistant that retrieves and analyzes emails, meetings/calendar, and OneDrive files via Microsoft Graph. It supports conversational queries with follow-ups, name resolution, real-time date handling, and optional AIXplain-powered features. The app launches directly in interactive mode and prints a clean Chat Output with readable item lines plus a concise Technical Details block.

## Highlights

- Real-time awareness (current date/time, relative dates)
- Conversational chat with follow-ups (short-term memory)
- Name-based queries (use names instead of emails)
- Intelligent last-email detection
- Retrieval and analysis for emails, meetings, and files
- Optional AIXplain integration with rule-based fallback
- Clean console output (no emojis, no summary/context blocks)

## Project Structure (simplified)

```
Core-Assistant-Pipeline/
├── agent/
│   ├── enhanced_smart_agent.py
│   └── advanced_analyzer.py
├── enhanced_assistant_master.py
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

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Create .env and fill:
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
```

3) Grant Microsoft Graph permissions (application) and admin consent. See APPLICATION_PERMISSIONS_README.md. Commonly required:
- Mail.Read
- Calendars.Read
- Files.Read.All (and often Sites.Read.All)
- OnlineMeetings.Read.All
- OnlineMeetingTranscript.Read.All (for transcripts)

## Run

Interactive mode:
```bash
python enhanced_assistant_master.py
```

Inside interactive mode:
- help shows examples
- time prints current date/time
- user switches the target user UPN
- quit exits

## Output format

Each query prints:
- Chat Output: natural response and Items list when applicable
  - Emails: From | Subject | Date | Attachments
  - Meetings: Subject | Organizer | Start | End | Attendees
  - Files: Name | Size MB | Modified | Type
- Technical Details: tool, question type, data count, timestamp, is follow-up

## Example queries

Emails
- emails from today
- emails from john.doe@domain.com today
- emails from John
- last email
- recent emails
- who sent the most emails last week

Meetings
- meetings today
- meetings this week
- meetings next week
- who organized the most meetings last month
- meeting transcript for id https://teams.microsoft.com/l/meetup-join/...

Files (OneDrive)
- list files
- list files in "Documents"
- download onedrive file "/Documents/Report.pdf" to "C:\\Users\\User\\Downloads\\Report.pdf"
- upload "./Local.docx" to "/Documents/Local.docx"

Follow-ups
- emails from John -> what about Sarah?
- and Mike too
- also show me recent files

## Notes on meeting transcripts (application permissions)

- Transcript API requires OnlineMeetingTranscript.Read.All (application). OnlineMeetings.Read.All helps locate meetings.
- Always call user-scoped endpoints with app-only tokens: /users/{USER_ID}/onlineMeetings/{meetingId}/transcripts
- Provide either a Teams join URL, a numeric conference id, or a calendar event id; the app attempts to resolve these to the correct onlineMeeting id.
- Transcription must have been enabled and started during the meeting.

## How it works (brief)

- Single agent: agent/enhanced_smart_agent.py
  - Optional AIXplain model for intent; rule-based fallback is always available
  - Real-time date parsing and last-email heuristics
  - NameResolver to map names to emails
  - Short-term conversation memory for follow-ups
  - AdvancedAnalyzer for basic natural-language insights

## License

MIT License – see LICENSE
