# Email and Calendar Management System

A comprehensive Python application for retrieving and processing emails and calendar events using Microsoft Graph API with advanced conversation thread support.

## Features

### Email Retrieval Functions (with Conversation Threads)
- **Email by ID**: Retrieve specific emails by their IDs with full conversation threads
- **Email by Sender & Date**: Find emails from a specific sender on a specific date with conversation threads
- **Email by Date Range**: Get all emails within a date range with conversation threads
- **Email by Subject & Date Range**: Search emails by subject keyword within a date range with conversation threads

### Calendar Event Retrieval Functions
- **Meetings by Date**: Retrieve all meetings on a specific date
- **Meetings by Organizer & Date**: Find meetings organized by a specific person on a specific date
- **Meetings by Date Range**: Get all meetings within a date range
- **Meetings by Subject & Date Range**: Search meetings by subject keyword within a date range

### Enhanced Email Processing
- **Conversation Thread Retrieval**: Automatically retrieves original emails and all replies in the conversation
- **Chronological Ordering**: All messages are sorted by received date/time
- **Deduplication**: Removes duplicate messages within conversations
- **Original vs Replies Option**: Choose to include or exclude original messages
- **Optimized Search**: Uses multiple strategies to efficiently find conversations

### Email Attachment Processing
- **Conversation-Wide Attachment Collection**: Extract attachments from original email AND all replies
- **Multiple File Format Support**: 
  - **Text files**: `.txt`, `.csv`, `.log`, `.md`, `.html`, `.xml`, `.json`
  - **Documents**: PDF, DOCX, XLSX, PPTX
- **Memory Efficient**: Processes attachments in memory without saving to disk
- **Interactive Interface**: Select and view multiple attachments from entire conversation threads
- **Automatic Library Installation**: Installs required libraries automatically
- **Attachment Source Tracking**: Shows which email each attachment comes from

### Calendar Event Processing
- **Comprehensive Meeting Details**: Retrieves subject, organizer, attendees, start/end times, location, and description
- **Flexible Search Options**: Search by date, organizer, subject, or date ranges
- **Client-Side Filtering**: Efficient filtering for organizer and subject searches
- **Detailed Meeting Information**: Shows meeting status, response status, and recurrence patterns

## Prerequisites

- Python 3.7 or higher
- Microsoft Azure AD application with appropriate permissions
- Microsoft Graph API access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arabaya3/Core-Assistant-Pipeline-.git
   cd Core-Assistant-Pipeline-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   CLIENT_ID=your_azure_app_client_id
   TENANT_ID=your_azure_tenant_id
   ```

## Configuration

### Azure AD Application Setup

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory → App registrations
3. Create a new application or use existing one
4. Add the following API permissions:
   - `Mail.Read` (Delegated)
   - `User.Read` (Delegated)
   - `Calendars.Read` (Delegated)
5. Grant admin consent for the permissions
6. Copy the Client ID and Tenant ID to your `.env` file

## Usage

### Email Management

#### Master Tool (Recommended)
Run the email master tool for an interactive menu with single authentication:
```bash
python email_retriever_master.py
```

#### Individual Email Functions

##### 1. Email Attachment Viewer (Conversation Thread)
```bash
python shared-files-simple.py
```
- Enter email ID to view attachments from entire conversation thread
- Select attachments to view their content
- Shows which email each attachment comes from
- Supports PDF, DOCX, XLSX, PPTX text extraction
- Collects attachments from original email and all replies

##### 2. Retrieve Emails by ID List (with Conversation Threads)
```bash
python email_by_id_retriever.py
```
- Enter multiple email IDs
- Returns original emails and all replies in conversation threads
- Option to exclude original messages and show only replies
- Shows recent email IDs for testing
- Enhanced error handling with detailed debugging

##### 3. Retrieve Emails by Sender and Date (with Conversation Threads)
```bash
python email_by_sender_date_retriever.py
```
- Enter sender email address
- Enter specific date (YYYY-MM-DD)
- Returns all emails from that sender on that date with conversation threads
- Uses client-side filtering to avoid API limitations
- Case-insensitive email matching

##### 4. Retrieve Emails by Date Range (with Conversation Threads)
```bash
python email_date_range_retriever.py
```
- Enter start date (YYYY-MM-DD)
- Enter end date (YYYY-MM-DD)
- Returns all emails within the date range with conversation threads
- Optimized to handle large mailboxes efficiently
- Shows email count per day

##### 5. Retrieve Emails by Subject and Date Range (with Conversation Threads)
```bash
python email_subject_date_range_retriever.py
```
- Enter subject keyword to search
- Enter start and end dates
- Returns emails containing the subject keyword within the date range
- Includes full conversation threads for each found email

### Calendar Management

#### Master Tool
Run the calendar master tool for an interactive menu:
```bash
python calendar_retriever_master.py
```

#### Individual Calendar Functions

##### 1. Get Meetings by Date
```bash
python calendar_by_date_retriever.py
```
- Enter specific date (YYYY-MM-DD)
- Returns all meetings scheduled on that date
- Shows meeting details including organizer, attendees, and location

##### 2. Retrieve Meetings by Organizer and Date
```bash
python calendar_by_organizer_date_retriever.py
```
- Enter organizer email address
- Enter specific date (YYYY-MM-DD)
- Returns meetings organized by that person on that date
- Case-insensitive organizer matching

##### 3. Retrieve All Meetings Within Date Range
```bash
python calendar_date_range_retriever.py
```
- Enter start date (YYYY-MM-DD)
- Enter end date (YYYY-MM-DD)
- Returns all meetings within the date range
- Shows meeting count per day

##### 4. Retrieve Meetings by Subject and Date Range
```bash
python calendar_subject_date_range_retriever.py
```
- Enter subject keyword to search
- Enter start and end dates
- Returns meetings containing the subject keyword within the date range
- Case-insensitive subject matching

## Example Outputs

### Email Retrieval with Conversation Threads
```
============================================================
Email ID Retriever (with Conversation Thread)
============================================================
Retrieving email 1/2: AAMkADUyNTM4ODIzLTAwNjQtNDIwNC1iYTg2LTg0ZGMxMzY2NDEyNQBGAAAAAABL8I8LFlz_SppGvRY2b9NjBwDZKKmYhKaWSZjnH3bi1_dMAAAAAAEJAADZKKmYhKaWSZjnH3bi1_dMAAFJAa4JAAA=

✓ Retrieved 5 message(s) in conversation.

Retrieved Conversation Messages:
============================================================
1. Subject: Project Update Meeting
   From: manager@company.com
   Date: 2025-01-15T10:30:00Z
   Has Attachments: Yes
   Preview: Hi team, please find attached the latest project update...
   ConversationId: AAQkADUyNTM4ODIzLTAwNjQtNDIwNC1iYTg2LTg0ZGMxMzY2NDEyNQAQAIyqjx8yfdJKon3-p5h5SIQ=

2. Subject: Re: Project Update Meeting
   From: team@company.com
   Date: 2025-01-15T11:15:00Z
   Has Attachments: No
   Preview: Thanks for the update. I have some questions...
   ConversationId: AAQkADUyNTM4ODIzLTAwNjQtNDIwNC1iYTg2LTg0ZGMxMzY2NDEyNQAQAIyqjx8yfdJKon3-p5h5SIQ=
```

### Calendar Event Retrieval
```
============================================================
Calendar Date Retriever
============================================================
Searching for meetings on: 2025-01-15
============================================================

Retrieved 8 meetings... (Total: 8)

Retrieved Meetings:
============================================================
1. Subject: Project Update Meeting
   Organizer: manager@company.com
   Start: 2025-01-15T10:00:00Z
   End: 2025-01-15T11:00:00Z
   Location: Conference Room A
   Attendees: 5 people
   Status: accepted

2. Subject: Team Standup
   Organizer: team@company.com
   Start: 2025-01-15T14:00:00Z
   End: 2025-01-15T14:30:00Z
   Location: Virtual Meeting
   Attendees: 8 people
   Status: accepted
```

### Attachment Viewer with Conversation Threads
```
============================================================
Email Attachment Viewer (Conversation Thread)
============================================================

Original Email Details:
Subject: Project Update Meeting
From: manager@company.com
Date: 2025-01-15T10:30:00Z

Retrieving conversation thread...
Found 5 messages in conversation thread

Processing message 1/5: Project Update Meeting
From: manager@company.com
Date: 2025-01-15T10:30:00Z
Found 2 attachments in this message
  ✓ Added: project_update.pdf
  ✓ Added: budget.xlsx

Processing message 2/5: Re: Project Update Meeting
From: team@company.com
Date: 2025-01-15T11:15:00Z
Found 1 attachments in this message
  ✓ Added: feedback.docx

============================================================
Total attachments found in conversation: 3
============================================================

All attachments in conversation:
================================================================================
 1. project_update.pdf (Document)
     From: manager@company.com
     Subject: Project Update Meeting
     Date: 2025-01-15T10:30:00Z

 2. budget.xlsx (Document)
     From: manager@company.com
     Subject: Project Update Meeting
     Date: 2025-01-15T10:30:00Z

 3. feedback.docx (Document)
     From: team@company.com
     Subject: Re: Project Update Meeting
     Date: 2025-01-15T11:15:00Z
```

### Calendar Search by Subject
```
============================================================
Calendar Subject Date Range Retriever
============================================================
Searching for meetings with subject containing: 'Project'
From: 2025-01-01
To: 2025-01-31
============================================================

Retrieved 45 meetings, filtered to 12 by subject... (Total filtered: 12)

Retrieved Meetings:
============================================================
1. Subject: Project Kickoff Meeting
   Organizer: manager@company.com
   Start: 2025-01-05T09:00:00Z
   End: 2025-01-05T10:00:00Z
   Location: Conference Room B
   Attendees: 10 people

2. Subject: Project Status Update
   Organizer: lead@company.com
   Start: 2025-01-15T14:00:00Z
   End: 2025-01-15T15:00:00Z
   Location: Virtual Meeting
   Attendees: 6 people
```

## File Structure

```
├── shared-files-simple.py              # Email attachment viewer (conversation threads)
├── email_by_id_retriever.py           # Retrieve emails by ID list (conversation threads)
├── email_by_sender_date_retriever.py  # Retrieve by sender and date (conversation threads)
├── email_date_range_retriever.py      # Retrieve by date range (conversation threads)
├── email_subject_date_range_retriever.py # Retrieve by subject and date range (conversation threads)
├── email_retriever_master.py          # Email master tool with menu (single authentication)
├── calendar_by_date_retriever.py      # Get meetings by specific date
├── calendar_by_organizer_date_retriever.py # Get meetings by organizer and date
├── calendar_date_range_retriever.py   # Get meetings within date range
├── calendar_subject_date_range_retriever.py # Get meetings by subject and date range
├── calendar_retriever_master.py       # Calendar master tool with menu
├── requirements.txt                    # Python dependencies
├── README.md                          # This documentation
└── .env                               # Environment variables (not in repo)
```

## Technical Improvements

### Email Features
- **Conversation Thread Retrieval**: Uses $search, msgfolderroot, inbox, and fallback methods
- **Optimized Performance**: Limits searches to recent messages to avoid timeouts
- **Robust Error Handling**: Graceful fallback when primary methods fail
- **Deduplication**: Removes duplicate messages within conversations

### Calendar Features
- **Microsoft Graph Calendar API**: Uses calendarView endpoint for efficient retrieval
- **Client-Side Filtering**: Filters organizer and subject searches locally
- **Comprehensive Meeting Data**: Retrieves all meeting details including attendees and location
- **Flexible Date Handling**: Supports various date formats and ranges

### Enhanced Search Methods
- **Client-Side Filtering**: Avoids API limitations and InefficientFilter errors
- **Case-Insensitive Matching**: Works with different email and organizer formats
- **Early Termination**: Stops searching when date range is exceeded
- **Progress Tracking**: Shows detailed progress during searches

### Authentication Improvements
- **Single Authentication**: Master tools authenticate once per session
- **Token Reuse**: Headers passed to all functions to avoid re-authentication
- **Better Error Messages**: Detailed error information for troubleshooting
- **Calendar Permissions**: Includes Calendars.Read permission for calendar access

## Supported File Types

### Text Files (Direct Reading)
- `.txt`, `.csv`, `.log`, `.md`, `.tex`, `.html`, `.htm`, `.xml`, `.json`

### Document Files (Text Extraction)
- **PDF** (`.pdf`) - Extracts text from all pages
- **Word** (`.docx`) - Extracts text from all paragraphs
- **Excel** (`.xlsx`, `.xls`) - Displays data in table format
- **PowerPoint** (`.pptx`, `.ppt`) - Extracts text from all slides

## Calendar Event Information

### Meeting Details Retrieved
- **Subject**: Meeting title and description
- **Organizer**: Person who created the meeting
- **Start/End Times**: Meeting duration in UTC
- **Location**: Physical or virtual meeting location
- **Attendees**: List of meeting participants
- **Response Status**: Whether you've accepted/declined
- **Meeting Status**: Whether the meeting is confirmed, tentative, etc.
- **Recurrence**: Information about recurring meetings
- **Description**: Detailed meeting notes and agenda

## Security Features

- **No File Downloads**: All processing happens in memory
- **Environment Variables**: Sensitive configuration stored in `.env` file
- **Memory-Only Processing**: No temporary files created
- **Secure Authentication**: Uses Microsoft's OAuth 2.0 flow
- **Single Authentication Session**: Reduces authentication prompts
- **Calendar Permissions**: Minimal required permissions for calendar access

## Dependencies

- `msal` - Microsoft Authentication Library
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `PyPDF2` - PDF text extraction (auto-installed)
- `python-docx` - Word document processing (auto-installed)
- `pandas` - Excel file processing (auto-installed)
- `python-pptx` - PowerPoint processing (auto-installed)

## Error Handling

The application includes comprehensive error handling for:
- Missing environment variables
- Authentication failures
- File format compatibility issues
- Network connectivity problems
- Library installation failures
- Invalid date formats
- Empty search results
- API rate limiting and InefficientFilter errors
- Conversation retrieval failures
- Attachment processing errors
- Calendar API errors
- Meeting retrieval failures

## Performance Optimizations

- **Limited Search Scope**: Searches only recent messages to avoid timeouts
- **Client-Side Filtering**: Reduces API calls and avoids complex server-side filters
- **Batch Processing**: Processes emails and meetings in batches for better performance
- **Early Termination**: Stops searching when criteria are met
- **Caching**: Reuses authentication tokens across functions
- **Calendar View API**: Uses efficient calendarView endpoint for meeting retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the GitHub repository. 