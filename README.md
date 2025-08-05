# Email Management System

A comprehensive Python application for retrieving and processing emails using Microsoft Graph API.

## Features

### Email Retrieval Functions
- **Email by ID**: Retrieve specific emails by their IDs
- **Email by Sender & Date**: Find emails from a specific sender on a specific date
- **Email by Date Range**: Get all emails within a date range
- **Email by Subject & Date Range**: Search emails by subject keyword within a date range

### Email Attachment Processing
- **Email Attachment Processing**: Extract text from email attachments without downloading files
- **Multiple File Format Support**: 
  - **Text files**: `.txt`, `.csv`, `.log`, `.md`, `.html`, `.xml`, `.json`
  - **Documents**: PDF, DOCX, XLSX, PPTX
- **Memory Efficient**: Processes attachments in memory without saving to disk
- **Interactive Interface**: Select and view multiple attachments from a single email
- **Automatic Library Installation**: Installs required libraries automatically

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
5. Grant admin consent for the permissions
6. Copy the Client ID and Tenant ID to your `.env` file

## Usage

### Master Tool (Recommended)
Run the master tool for an interactive menu:
```bash
python email_retriever_master.py
```

### Individual Functions

#### 1. Email Attachment Viewer
```bash
python shared-files-simple.py
```
- Enter email ID to view attachments
- Select attachments to view their content
- Supports PDF, DOCX, XLSX, PPTX text extraction

#### 2. Retrieve Emails by ID List
```bash
python email_by_id_retriever.py
```
- Enter multiple email IDs
- Returns detailed information for each email

#### 3. Retrieve Emails by Sender and Date
```bash
python email_by_sender_date_retriever.py
```
- Enter sender email address
- Enter specific date (YYYY-MM-DD)
- Returns all emails from that sender on that date

#### 4. Retrieve Emails by Date Range
```bash
python email_date_range_retriever.py
```
- Enter start date (YYYY-MM-DD)
- Enter end date (YYYY-MM-DD)
- Returns all emails within the date range
- Shows email count per day

#### 5. Retrieve Emails by Subject and Date Range
```bash
python email_subject_date_range_retriever.py
```
- Enter subject keyword to search
- Enter start and end dates
- Returns emails containing the subject keyword within the date range

## Example Outputs

### Email Retrieval
```
============================================================
Email ID Retriever
============================================================
Retrieving email 1/2: AAMkADUyNTM4ODIzLTAwNjQtNDIwNC1iYTg2LTg0ZGMxMzY2NDEyNQBGAAAAAABL8I8LFlz_SppGvRY2b9NjBwDZKKmYhKaWSZjnH3bi1_dMAAAAAAEJAADZKKmYhKaWSZjnH3bi1_dMAAFJAa4JAAA=

✓ Retrieved: Project Update Meeting

Retrieved Emails:
============================================================
1. Subject: Project Update Meeting
   From: manager@company.com
   Date: 2025-01-15T10:30:00Z
   Has Attachments: Yes
   Preview: Hi team, please find attached the latest project update...
```

### Date Range Search
```
============================================================
Email Date Range Retriever
============================================================
Searching for emails from: 2025-01-01
To: 2025-01-31
============================================================

Found 45 emails in date range 2025-01-01 to 2025-01-31
============================================================

Search Summary
============================================================
Date Range: 2025-01-01 to 2025-01-31
Total emails found: 45

Emails per day:
  2025-01-01: 3 emails
  2025-01-02: 5 emails
  2025-01-03: 2 emails
  ...
```

## File Structure

```
├── shared-files-simple.py              # Email attachment viewer
├── email_by_id_retriever.py           # Retrieve emails by ID list
├── email_by_sender_date_retriever.py  # Retrieve by sender and date
├── email_date_range_retriever.py      # Retrieve by date range
├── email_subject_date_range_retriever.py # Retrieve by subject and date range
├── email_retriever_master.py          # Master tool with menu
├── requirements.txt                    # Python dependencies
├── README.md                          # This documentation
└── .env                               # Environment variables (not in repo)
```

## Supported File Types

### Text Files (Direct Reading)
- `.txt`, `.csv`, `.log`, `.md`, `.tex`, `.html`, `.htm`, `.xml`, `.json`

### Document Files (Text Extraction)
- **PDF** (`.pdf`) - Extracts text from all pages
- **Word** (`.docx`) - Extracts text from all paragraphs
- **Excel** (`.xlsx`, `.xls`) - Displays data in table format
- **PowerPoint** (`.pptx`, `.ppt`) - Extracts text from all slides

## Security Features

- **No File Downloads**: All processing happens in memory
- **Environment Variables**: Sensitive configuration stored in `.env` file
- **Memory-Only Processing**: No temporary files created
- **Secure Authentication**: Uses Microsoft's OAuth 2.0 flow

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