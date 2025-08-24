# Email Agent System

A comprehensive email management system that provides intelligent email search and retrieval capabilities through Microsoft Graph API integration with AIXplain agent deployment.

## Features

- **Email Search by Sender**: Find emails from specific people or email addresses
- **Email Search by Subject**: Locate emails containing specific keywords in the subject line
- **Email Details by ID**: Retrieve complete information about specific emails by ID
- **Flask API Server**: RESTful API endpoints for email operations
- **AIXplain Agent Integration**: Deployed intelligent email assistant agent
- **Natural Language Processing**: Understand user intent and translate to API calls
- **Comprehensive Error Handling**: Robust error handling and user-friendly messages
- **Environment Variable Configuration**: Secure credential management using .env files

## Project Structure

```
email-agent-system/
├── app.py                    # Flask API server
├── email_agent_example.py    # Python email agent implementation
├── test_email_agent.py       # Test suite for email agent
├── Agents/
│   └── Prompt.py            # AIXplain agent deployment script
├── Email_Tools/             # Email search utilities
│   ├── email_by_sender.py
│   ├── email_by_subject.py
│   └── email_by_id.py
├── OneDrive_Tools/          # OneDrive file management
│   ├── list_onedrive_files.py
│   ├── list_shared_files.py
│   └── retrieve_file_by_name.py
├── templates/               # Web interface templates
│   └── index.html
├── utils/                   # Utility functions
│   └── authentication.py
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with your Microsoft Graph API credentials:
   ```
   CLIENT_ID=your_client_id
   TENANT_ID=your_tenant_id
   CLIENT_SECRET=your_client_secret
   DEFAULT_USER_ID=your_email@domain.com
   AIXPLAIN_API_KEY=your_aixplain_api_key
   ```

## Environment Variables

### Required Variables:
- `CLIENT_ID`: Microsoft Graph API Client ID
- `TENANT_ID`: Microsoft Azure Tenant ID  
- `CLIENT_SECRET`: Microsoft Graph API Client Secret
- `DEFAULT_USER_ID`: Default email user
- `AIXPLAIN_API_KEY`: AIXplain platform API key

## Usage

### Starting the Flask API Server

```bash
python app.py
```

The server will start on `http://localhost:5000` with the following endpoints:
- `GET /api/emails/sender/{sender}` - Search emails by sender
- `GET /api/emails/subject/{subject}` - Search emails by subject
- `GET /api/emails/id/{email_id}` - Get email details by ID
- `GET /api/health` - Health check

### Using the Python Email Agent

```python
from email_agent_example import EmailAgent

agent = EmailAgent()
response = agent.answer_query("Find emails from john@example.com")
print(response)
```

### Testing the Email Agent

```bash
# Run automated tests
python test_email_agent.py

# Run interactive mode
python test_email_agent.py --interactive
```

### Deploying the AIXplain Agent

```bash
python Agents/Prompt.py
```

This deploys the "Email Search Agent v2" to your AIXplain platform.

## API Endpoints

### Search by Sender
```http
GET /api/emails/sender/john@example.com
```

### Search by Subject
```http
GET /api/emails/subject/meeting
```

### Get Email Details
```http
GET /api/emails/id/AAMkAGI2TG93AAA=
```

## Example Queries

### Email Search Queries:
- "Find emails from john@example.com"
- "Show me emails about meetings"
- "Get emails with subject project"
- "Find messages about budget"
- "Show emails from noreply@microsoft.com"

### Natural Language Queries:
- "What emails did I receive from John yesterday?"
- "Show me all meeting-related emails from this week"
- "Find emails about the quarterly report"
- "Get emails from my manager about the project"

## Response Format

All API responses return JSON with a "result" field containing the email data:

```json
{
  "result": "=== Emails from john@example.com ===\n..."
}
```

## Error Handling

The system provides comprehensive error handling:
- Invalid email addresses
- Non-existent subjects
- API authentication errors
- Network connectivity issues
- Rate limiting

## Security and Privacy

- All credentials stored in environment variables
- Microsoft Graph API authentication
- Secure HTTP requests
- User privacy protection
- No email content logging

## Troubleshooting

### Common Issues:

1. **Server not starting**: Check environment variables in `.env` file
2. **Authentication errors**: Verify Microsoft Graph API credentials
3. **No results found**: Check email address format and existence
4. **API timeouts**: Increase timeout settings in configuration

### Debug Mode:

Enable debug logging by setting `DEBUG=true` in your environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
