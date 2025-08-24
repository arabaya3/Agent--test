## Core Pipeline Tools (Microsoft 365)

This project is a menu-driven toolbox for working with Microsoft 365 via Microsoft Graph. It supports:

- Email tools: retrieve emails by IDs, sender, subject, date ranges; view and extract attachments
- Calendar tools: query meetings by date, date range, organizer, or subject
- Meeting tools: look up meetings by ID or title, fetch participation/attendance, and retrieve transcripts (saved to `saved_transcripts/`)
- OneDrive tools: list, download, upload files; view items shared with you (delegated)

All tools are CLI-based and run directly from the terminal.


### Requirements

- Python 3.9+
- An Azure AD app registration with appropriate Microsoft Graph permissions (see Permissions)
- Windows, macOS, or Linux (examples assume Windows PowerShell)
- Packages: `requests`, `python-dotenv`, `msal` (and optionally `python-docx` for DOCX transcript export)


### Installation

1) Clone and enter the project directory

```powershell
git clone https://github.com/arabaya3/Agent--test.git
cd Core_Pipline
```

2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies

```powershell
pip install -r requirements.txt
```


### Environment configuration

Create a file named `.env` in the project root with the following variables. Values depend on your Azure app(s) and tenant.

```ini
# App-only (application) auth — used by email/calendar/onedrive and attendance tools
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET=your_client_secret

# Target user mailbox/drive for app-only operations
# Use a UPN (email) or object ID; many tools require this
DEFAULT_USER_ID=user@contoso.com

# Optional: debug and beta flags
DEBUG_AUTH=0              # set to 1/true to print token diagnostics
USE_GRAPH_BETA=0          # set to 1 to allow beta endpoints in transcript tool when needed

# Delegated (user) auth — used by transcript tool (device code flow)
# Use a Public client app with "Allow public client flows" enabled (no secret)
# The transcript tool reads CLIENT_ID (public client) and uses device code; no CLIENT_SECRET is needed.
DELEGATED_SCOPES=User.Read OnlineMeetings.Read OnlineMeetingTranscript.Read.All
# Optional: change where the device-code token cache is stored
TOKEN_CACHE_PATH=%USERPROFILE%\.msal\transcript_tool_cache.bin
```


### Permissions (Microsoft Graph)

Grant these permissions to your Azure app(s), then click “Grant admin consent”. Application permissions are used for most tools; transcripts use delegated permissions.

- Email tools (read messages and attachments)
  - Application: `Mail.Read`

- Calendar tools (read events)
  - Application: `Calendars.Read`

- Meeting tools
  - Lookups by ID/title: Application: `Calendars.Read`
  - Attendance reports (by meeting ID/join URL/event ID): Application: `OnlineMeetings.Read.All`
  - Transcripts (delegated via device code): Delegated scopes such as `User.Read`, `OnlineMeetings.Read`, `OnlineMeetingTranscript.Read.All`

- OneDrive tools (app-only mailbox/drive operations)
  - List/Download: Application: `Files.Read.All`
  - Upload: Application: `Files.ReadWrite.All`

- OneDrive “Shared with me” (delegated, user sign-in required)
  - Delegated: `Files.Read` (expand as needed), plus `offline_access`

Notes:
- App-only (application) tokens call `/users/{DEFAULT_USER_ID}/...` rather than `/me`.
- Delegated flows operate as the signed-in user and use `/me/...` endpoints.


### Running the toolbox

From the project root:

```powershell
python main.py
```

You’ll see a menu with four categories: Email, Calendar, Meeting, OneDrive. Navigate with the on-screen prompts.


### Running individual tools directly

You can also run specific tools without the main menu:

```powershell
python email_tools\by_id.py
python email_tools\by_date_range.py
python email_tools\by_sender_date.py
python email_tools\by_subject_date_range.py

python calendar_tools\by_date.py
python calendar_tools\by_organizer_date.py
python calendar_tools\by_date_range.py
python calendar_tools\by_subject_date_range.py

python meeting_tools\by_id.py
python meeting_tools\by_title.py
python meeting_tools\attendance.py
python meeting_tools\transcript.py

python onedrive_tools\list_files.py
python onedrive_tools\retrieve_files.py
python onedrive_tools\upload_files.py
python onedrive_tools\shared_with_me.py   # delegated auth
```


### Tool details and expected prompts

- Email tools (application permissions)
  - `by_id.py`: Shows recent email IDs, lets you pick messages, then prints the full conversation thread with cleaned body text.
  - `by_date_range.py`: Prompts for how many recent IDs to cache, then a start/end date; fetches messages and their conversation threads.
  - `by_sender_date.py`, `by_subject_date_range.py`: Filter by sender or subject within date ranges.
  - `shared_files_simple.py`: For a given email ID, pulls document attachments from the entire conversation and attempts text extraction for viewing in the console.

- Calendar tools (application permissions)
  - `by_date.py`, `by_date_range.py`: Retrieve events in the specified window.
  - `by_organizer_date.py`: Filter by organizer on a given date.
  - `by_subject_date_range.py`: Filter by subject across a date range.

- Meeting tools
  - `by_id.py`, `by_title.py`: Find and display meeting details (application: `Calendars.Read`).
  - `attendance.py`: Enter an onlineMeeting ID, Teams join URL, or calendar event ID; the tool resolves it to an onlineMeeting and fetches attendance reports with detailed records (application: `OnlineMeetings.Read.All`).
  - `transcript.py` (delegated): Device-code sign-in, accepts a join URL, joinMeetingId, or onlineMeeting ID; resolves and downloads the latest transcript. Saves under `saved_transcripts/` as `{MeetingName}_transctipt.vtt` or `.docx`. Default delegated scopes come from `DELEGATED_SCOPES`. Install `python-docx` to export DOCX; otherwise VTT is saved.

- OneDrive tools
  - `list_files.py` (application): Lists items in a user’s drive or a subfolder under `/users/{DEFAULT_USER_ID}/drive`.
  - `retrieve_files.py` (application): Downloads a file by path; optionally saves locally and prints metadata.
  - `upload_files.py` (application): Uploads a local file to a destination path; supports small and large files (chunked).
  - `shared_with_me.py` (delegated): Signs in a user (device code or ROPC), lists items shared-with-me, and allows viewing text content. Requires a public client and delegated scopes.


### Common setup pitfalls and fixes

- 403 Forbidden / access denied
  - Ensure the app has the exact application permissions listed above, and that admin consent has been granted in Azure Portal.
  - App-only tokens must target a specific user with `/users/{DEFAULT_USER_ID}/...`; set `DEFAULT_USER_ID` in `.env`.
  - For attendance (application), confirm `OnlineMeetings.Read.All`.
  - For transcript (delegated), confirm the delegated scopes include `OnlineMeetings.Read` and `OnlineMeetingTranscript.Read.All`. The tool filters out reserved scopes automatically.

- 404 Not found for messages/events/files
  - Confirm `DEFAULT_USER_ID` points to the correct mailbox/OneDrive account and that the resource exists in that tenant.

- Delegated “Shared with me” errors
  - Provide `PUBLIC_CLIENT_ID` (no secret), and either:
    - Device Code: set none or only `GRAPH_USERNAME` to hint the account, then follow the printed instructions, or
    - ROPC: set both `GRAPH_USERNAME` and `GRAPH_PASSWORD` (only if your tenant allows it and the account has no MFA).
  - Ensure delegated scopes (e.g., `Files.Read`, `offline_access`) are configured.

- Empty or truncated email body
  - Some messages are HTML-heavy; tools attempt basic HTML cleanup. Body may be empty if content is not accessible or is attachment-only.

- Rate limits / large result sets
  - Tools include paging and reasonable limits; narrow your filters if you hit limits.

### Transcript tool CLI examples (delegated)

```powershell
# Default VTT
python meeting_tools\transcript.py "https://teams.microsoft.com/l/meetup-join/..."

# Explicit format
python meeting_tools\transcript.py "19:meeting_...@thread.v2" --format vtt
python meeting_tools\transcript.py "19:meeting_...@thread.v2" --format docx   # requires python-docx
```

Transcripts are saved under `saved_transcripts/` with the meeting subject as the filename prefix.


### Development

- Code style: Black/Flake8 are included in `requirements.txt`.
- Static typing: A `pyrightconfig.json` is included; you can run your preferred type checker.


### Quick checklist

1) Create `.env` with app-only credentials and `DEFAULT_USER_ID`
2) Grant Graph app permissions + admin consent
3) `pip install -r requirements.txt`
4) `python main.py` (or run a specific tool)
5) For `shared_with_me.py`, add delegated config (`PUBLIC_CLIENT_ID`, optional `GRAPH_USERNAME`/`GRAPH_PASSWORD`) and sign in


### Disclaimer

Use this toolkit responsibly within your organization’s security and compliance policies. Some features require elevated app permissions; coordinate with your Azure AD administrators to grant only what is necessary.


