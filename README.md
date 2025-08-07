# Assistant Retriever Master

A unified Python assistant for retrieving and processing emails, calendar events, and meetings using the Microsoft Graph API.

## Features

- Retrieve emails by ID, sender/date, date range, or subject/date range
- Retrieve calendar meetings by date, organizer/date, date range, or subject/date range
- Retrieve meeting details by ID, by title, get transcript, audience, and attendance
- Interactive command-line menu for all features
- Microsoft OAuth2 authentication (device code flow)
- Works with Office 365/Outlook accounts

## Project Structure

```
Core-Assistant-Pipeline-/
├── assistant_retriever_master.py      # Main entry point (menu for all tools)
├── email_tools/
│   ├── by_id.py
│   ├── by_sender_date.py
│   ├── by_date_range.py
│   ├── by_subject_date_range.py
│   ├── shared_email_ids.py
│   └── __init__.py
├── calendar_tools/
│   ├── by_date.py
│   ├── by_organizer_date.py
│   ├── by_date_range.py
│   ├── by_subject_date_range.py
│   └── __init__.py
├── meeting_tools/
│   ├── by_id.py
│   ├── by_title.py
│   ├── transcript.py
│   ├── audience.py
│   ├── attendance.py
│   └── __init__.py
├── shared/
│   ├── shared_files_simple.py
│   └── __init__.py
├── .env
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Core-Assistant-Pipeline-
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Create a `.env` file in the project root:
     ```
     CLIENT_ID=your_azure_app_client_id
     TENANT_ID=your_azure_tenant_id
     ```
   - Register an Azure AD app and grant it the necessary Microsoft Graph API permissions (Mail.Read, Calendars.Read, OnlineMeetings.Read.All, etc.)

## Usage

Run the main assistant menu:
```bash
python3 assistant_retriever_master.py
```
Follow the interactive prompts to use email, calendar, or meeting tools.

## Requirements
- Python 3.7+
- Microsoft 365/Azure AD account with API access
- Required Python packages (see requirements.txt)

## License
MIT 