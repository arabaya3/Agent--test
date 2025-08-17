# Core Assistant Pipeline

A unified Python assistant for retrieving and processing emails, calendar events, meetings, and OneDrive files using the Microsoft Graph API with AI-powered query routing.

## 🚀 Features

- **🤖 AI-Powered Query Routing**: Uses AIXplain models for intelligent query interpretation and tool selection
- **📧 Email Management**: Retrieve emails by ID, sender/date, date range, or subject/date range
- **📅 Calendar Management**: Retrieve calendar meetings by date, organizer/date, date range, or subject/date range
- **🎯 Meeting Analytics**: Retrieve meeting details by ID, by title, get transcript, audience, and attendance
- **☁️ OneDrive Integration**: List, download, and upload files to OneDrive
- **🖥️ Interactive Command-Line Interface**: Menu-driven interface for all features
- **🔐 Microsoft OAuth2 Authentication**: Device code flow for secure access
- **🔄 Fallback Rule-Based Logic**: Intelligent routing when AI models are unavailable
- **⚡ Caching System**: Efficient email ID caching for improved performance

## 📁 Project Structure

```
Core-Assistant-Pipeline/
├── agent/
│   ├── core_agent.py              # AI-powered query router and main agent
│   └── __init__.py
├── assistant_retriever_master.py  # Main entry point (menu for all tools)
├── email_tools/
│   ├── by_id.py                   # Retrieve emails by specific IDs
│   ├── by_sender_date.py          # Retrieve emails from sender on date
│   ├── by_date_range.py           # Retrieve emails within date range
│   ├── by_subject_date_range.py   # Retrieve emails by subject and date range
│   ├── shared_email_ids.py        # Shared email ID caching utilities
│   └── __init__.py
├── calendar_tools/
│   ├── by_date.py                 # Get meetings on specific date
│   ├── by_organizer_date.py       # Get meetings by organizer on date
│   ├── by_date_range.py           # Get meetings within date range
│   ├── by_subject_date_range.py   # Get meetings by subject and date range
│   └── __init__.py
├── meeting_tools/
│   ├── by_id.py                   # Get meeting details by ID
│   ├── by_title.py                # Get meetings by title
│   ├── transcript.py              # Get meeting transcript by meeting ID
│   ├── audience.py                # Get meeting attendees by meeting ID
│   ├── attendance.py              # Get meeting attendance reports by meeting ID
│   └── __init__.py
├── onedrive_tools/
│   ├── list_files.py              # List files in OneDrive folder
│   ├── retrieve_files.py          # Download files from OneDrive
│   ├── upload_files.py            # Upload files to OneDrive
│   └── __init__.py
├── shared/
│   ├── auth.py                    # Microsoft Graph authentication utilities
│   ├── shared_files_simple.py     # Shared file utilities
│   └── __init__.py
├── .env                           # Environment variables (create this)
├── requirements.txt               # Python dependencies
├── AIXPLAIN_SETUP.md              # AIXplain configuration guide
├── APPLICATION_PERMISSIONS_README.md # Microsoft Graph permissions guide
├── ENV_SETUP_INSTRUCTIONS.md      # Environment setup instructions
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🛠️ Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Core-Assistant-Pipeline
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Microsoft Graph API Configuration
CLIENT_ID=your_azure_app_client_id
TENANT_ID=your_azure_tenant_id

# AIXplain Configuration (Optional - for AI-powered routing)
AIXPLAIN_API_KEY=your_aixplain_api_key
AIXPLAIN_MODEL_ID=your_aixplain_model_id
TEAM_API_KEY=your_team_api_key
```

### 4. Azure AD App Registration
Register an Azure AD app and grant it the necessary Microsoft Graph API permissions:
- `Mail.Read` - For email operations
- `Calendars.Read` - For calendar operations  
- `OnlineMeetings.Read.All` - For meeting operations
- `Files.ReadWrite.All` - For OneDrive operations

See `APPLICATION_PERMISSIONS_README.md` for detailed setup instructions.

## 🎯 Usage

### Interactive Menu Interface
Run the main assistant menu:
```bash
python assistant_retriever_master.py
```
Follow the interactive prompts to use email, calendar, meeting, or OneDrive tools.

### AI-Powered Agent
Use the intelligent agent for natural language queries:
```bash
python -c "from agent.core_agent import handle_query; print(handle_query('emails from john@example.com on 2025-08-10'))"
```

### Example Queries
The AI agent can understand natural language queries like:
- "emails from john@example.com on 2025-08-10"
- "meetings from 2025-08-01 to 2025-08-15"
- "list files in Documents folder"
- "download file.txt from OneDrive"
- "upload report.pdf to OneDrive"
- "get meeting transcript for meeting-id-123"
- "show attendance for meeting-id-456"

## 🛠️ Available Tools

### Email Tools
- `email_by_id` - Retrieve emails by specific IDs
- `email_by_sender_date` - Retrieve emails from a specific sender on a specific date
- `email_by_date_range` - Retrieve emails within a date range
- `email_by_subject_date_range` - Retrieve emails with specific subject within a date range

### Calendar Tools
- `calendar_by_date` - Get meetings on a specific date
- `calendar_by_organizer_date` - Get meetings organized by someone on a specific date
- `calendar_by_date_range` - Get meetings within a date range
- `calendar_by_subject_date_range` - Get meetings with specific subject within a date range

### Meeting Tools
- `meeting_by_id` - Get meeting details by ID
- `meeting_by_title` - Get meetings by title
- `meeting_transcript` - Get meeting transcript by meeting ID
- `meeting_audience` - Get meeting attendees by meeting ID
- `meeting_attendance` - Get meeting attendance reports by meeting ID

### OneDrive Tools
- `onedrive_list` - List files in OneDrive folder
- `onedrive_download` - Download a file from OneDrive
- `onedrive_upload` - Upload a file to OneDrive

## 📦 Dependencies

### Required Python Packages
- **msal** (>=1.20.0) - Microsoft Authentication Library for OAuth2
- **python-dotenv** (>=1.0.0) - Environment variable management
- **aixplain** (>=0.1.0) - AI-powered query routing
- **requests** (>=2.28.0) - HTTP requests for API calls

### System Requirements
- Python 3.7+
- Microsoft 365/Azure AD account with API access
- AIXplain account (optional - for AI-powered routing)

## 📚 Configuration Files

- `AIXPLAIN_SETUP.md` - Detailed AIXplain configuration guide
- `APPLICATION_PERMISSIONS_README.md` - Microsoft Graph API permissions setup
- `ENV_SETUP_INSTRUCTIONS.md` - Environment variable configuration guide

## 🔧 Development

### Testing the Agent
```bash
python -c "from agent.core_agent import test_aixplain_connection; test_aixplain_connection()"
```

### Running Individual Tools
Each tool can be imported and used independently:
```python
from email_tools.by_date_range import retrieve_emails_by_date_range
from calendar_tools.by_date import retrieve_meetings_by_date
from onedrive_tools.list_files import list_onedrive_files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the configuration guides in the documentation files
2. Verify your Azure AD app permissions
3. Ensure all dependencies are installed
4. Check your `.env` file configuration 