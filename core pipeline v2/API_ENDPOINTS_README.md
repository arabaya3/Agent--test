# Core Pipeline API v2.0 - Complete Endpoint Documentation

This document provides comprehensive documentation for all API endpoints in the Core Pipeline API v2.0.

## Base URL
```
http://localhost:5000
```

## Authentication
All endpoints require Microsoft Graph API authentication. Ensure your `.env` file contains:
- `TENANT_ID`
- `CLIENT_ID` 
- `CLIENT_SECRET`
- `DEFAULT_USER_ID`

## Endpoints Overview

### 1. Health & Documentation
- `GET /api/health` - Health check
- `GET /api/docs` - Complete API documentation

### 2. Email Tools
- `GET /api/emails/sender/<sender>` - Search emails by sender
- `GET /api/emails/id/<email_id>` - Get email by ID
- `GET /api/emails/subject/<subject>` - Search emails by subject
- `POST /api/emails/search` - Flexible email search

### 3. Calendar Tools
- `GET /api/calendar/date/<date>` - Get meetings by date
- `GET /api/calendar/organizer/<organizer>/date/<date>` - Search meetings by organizer and date
- `GET /api/calendar/subject/<subject>/start/<start_date>/end/<end_date>` - Search meetings by subject and date range

### 4. Meeting Tools
- `GET /api/meetings/id/<meeting_id>` - Get meeting details by ID
- `GET /api/meetings/title/<title>` - Search meetings by title
- `GET /api/meetings/attendance/<meeting_id>` - Get meeting attendance
- `GET /api/meetings/audience/<meeting_id>` - Get meeting audience
- `GET /api/meetings/transcript/<meeting_id>` - Get meeting transcript

### 5. OneDrive Tools
- `GET /api/onedrive/files` - List OneDrive files
- `GET /api/onedrive/shared` - List shared files
- `GET /api/onedrive/file/<file_name>` - Retrieve file by name

---

## Detailed Endpoint Documentation

### Health & Documentation

#### GET /api/health
Health check endpoint to verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Core Pipeline API is running"
}
```

#### GET /api/docs
Returns complete API documentation with all available endpoints.

**Response:**
```json
{
  "message": "Core Pipeline API Server",
  "version": "2.0.0",
  "endpoints": {
    "Email Tools": { ... },
    "Calendar Tools": { ... },
    "Meeting Tools": { ... },
    "OneDrive Tools": { ... }
  }
}
```

### Email Tools

#### GET /api/emails/sender/<sender>
Search emails by sender email address or name.

**Parameters:**
- `sender` (path): Email address or name to search for

**Example:**
```
GET /api/emails/sender/john@example.com
```

**Response:**
```json
{
  "result": "=== Emails from john@example.com ===\n\nFound 5 emails:\n..."
}
```

#### GET /api/emails/id/<email_id>
Get detailed email information by ID.

**Parameters:**
- `email_id` (path): Email ID

**Example:**
```
GET /api/emails/id/AAMkAGI2TG93AAA=
```

#### GET /api/emails/subject/<subject>
Search emails by subject line.

**Parameters:**
- `subject` (path): Subject keyword to search for

**Example:**
```
GET /api/emails/subject/meeting
```

#### POST /api/emails/search
Flexible email search with POST request.

**Request Body:**
```json
{
  "search_type": "sender|id|subject",
  "query": "search term or email id"
}
```

**Example:**
```json
{
  "search_type": "sender",
  "query": "john@example.com"
}
```

### Calendar Tools

#### GET /api/calendar/date/<date>
Get all meetings for a specific date.

**Parameters:**
- `date` (path): Date in YYYY-MM-DD format

**Example:**
```
GET /api/calendar/date/2024-01-15
```

#### GET /api/calendar/organizer/<organizer>/date/<date>
Search meetings by organizer and date.

**Parameters:**
- `organizer` (path): Organizer email address
- `date` (path): Date in YYYY-MM-DD format

**Example:**
```
GET /api/calendar/organizer/john@example.com/date/2024-01-15
```

#### GET /api/calendar/subject/<subject>/start/<start_date>/end/<end_date>
Search meetings by subject and date range.

**Parameters:**
- `subject` (path): Subject keyword to search for
- `start_date` (path): Start date in YYYY-MM-DD format
- `end_date` (path): End date in YYYY-MM-DD format

**Example:**
```
GET /api/calendar/subject/meeting/start/2024-01-01/end/2024-01-31
```

### Meeting Tools

#### GET /api/meetings/id/<meeting_id>
Get meeting details by ID.

**Parameters:**
- `meeting_id` (path): Meeting ID (can be Teams URL, event ID, or onlineMeeting ID)

**Example:**
```
GET /api/meetings/id/123456789
```

#### GET /api/meetings/title/<title>
Search meetings by title.

**Parameters:**
- `title` (path): Meeting title to search for

**Example:**
```
GET /api/meetings/title/weekly
```

#### GET /api/meetings/attendance/<meeting_id>
Get meeting attendance information.

**Parameters:**
- `meeting_id` (path): Meeting ID

**Example:**
```
GET /api/meetings/attendance/123456789
```

#### GET /api/meetings/audience/<meeting_id>
Get meeting audience information.

**Parameters:**
- `meeting_id` (path): Meeting ID

**Example:**
```
GET /api/meetings/audience/123456789
```

#### GET /api/meetings/transcript/<meeting_id>
Get meeting transcript.

**Parameters:**
- `meeting_id` (path): Meeting ID

**Example:**
```
GET /api/meetings/transcript/123456789
```

### OneDrive Tools

#### GET /api/onedrive/files
List OneDrive files.

**Query Parameters:**
- `folder_path` (optional): Folder path to search in
- `top` (optional): Number of files to return (default: 20)

**Example:**
```
GET /api/onedrive/files?folder_path=Documents&top=10
```

#### GET /api/onedrive/shared
List shared files.

**Query Parameters:**
- `top` (optional): Number of files to return (default: 20)

**Example:**
```
GET /api/onedrive/shared?top=10
```

#### GET /api/onedrive/file/<file_name>
Retrieve file by name.

**Parameters:**
- `file_name` (path): Name of the file to retrieve

**Query Parameters:**
- `folder_path` (optional): Folder path to search in

**Example:**
```
GET /api/onedrive/file/document.pdf?folder_path=Documents
```

---

## Error Handling

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "error": "Parameter is required"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error message from the tool"
}
```

**404 Not Found:**
```json
{
  "error": "Endpoint not found"
}
```

---

## Usage Examples

### Python Requests
```python
import requests

# Search emails by sender
response = requests.get("http://localhost:5000/api/emails/sender/john@example.com")
emails = response.json()

# Get calendar meetings for a date
response = requests.get("http://localhost:5000/api/calendar/date/2024-01-15")
meetings = response.json()

# Search meetings by title
response = requests.get("http://localhost:5000/api/meetings/title/weekly")
meetings = response.json()

# List OneDrive files
response = requests.get("http://localhost:5000/api/onedrive/files?top=10")
files = response.json()
```

### cURL
```bash
# Health check
curl http://localhost:5000/api/health

# Search emails
curl http://localhost:5000/api/emails/sender/john@example.com

# Get calendar meetings
curl http://localhost:5000/api/calendar/date/2024-01-15

# List OneDrive files
curl "http://localhost:5000/api/onedrive/files?top=10"
```

---

## Testing

Run the test script to verify all endpoints:
```bash
python test_all_endpoints.py
```

---

## Notes

1. **Authentication**: All endpoints require valid Microsoft Graph API credentials in your `.env` file.

2. **Rate Limiting**: Be mindful of Microsoft Graph API rate limits when making multiple requests.

3. **Date Formats**: All dates must be in YYYY-MM-DD format.

4. **File Paths**: OneDrive folder paths use forward slashes (/) and are relative to the root.

5. **Meeting IDs**: Meeting tools accept various ID formats including Teams URLs, event IDs, and onlineMeeting IDs.

6. **Error Handling**: All tools return descriptive error messages when authentication fails or data is not found.
