# Email Tools API Server

A Flask-based REST API server that provides email search and retrieval capabilities through Microsoft Graph API integration.

## Features

- **Email Search by Sender**: Find emails from specific people or email addresses
- **Email Search by Subject**: Locate emails containing specific keywords in the subject line
- **Email Details by ID**: Retrieve complete information about specific emails by ID
- **Flexible Search**: Advanced search with JSON payload support
- **Web Interface**: Built-in HTML interface for testing
- **Health Monitoring**: Server health check endpoint
- **Error Handling**: Comprehensive error handling and validation
- **Environment Configuration**: Secure credential management

## Prerequisites

- Python 3.7+
- Microsoft Graph API credentials
- Required environment variables in `.env` file

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file with your Microsoft Graph API credentials and public base URL for external access:
   ```
   CLIENT_ID=your_client_id
   TENANT_ID=your_tenant_id
   CLIENT_SECRET=your_client_secret
   DEFAULT_USER_ID=your_email@domain.com
   PUBLIC_BASE_URL=http://localhost:5000
   ```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Email Tools API is running"
}
```

### Search by Sender
```http
GET /api/emails/sender/{sender}
```

**Parameters:**
- `sender` (path): Email address or name to search for

**Response:**
```json
{
  "result": "=== Emails from john@example.com ===\n..."
}
```

### Search by Subject
```http
GET /api/emails/subject/{subject}
```

**Parameters:**
- `subject` (path): Subject keywords to search for

**Response:**
```json
{
  "result": "=== Email Search Results for: 'meeting' ===\n..."
}
```

### Get Email Details by ID
```http
GET /api/emails/id/{email_id}
```

**Parameters:**
- `email_id` (path): Microsoft Graph API email ID

**Response:**
```json
{
  "result": "=== Email Details ===\n..."
}
```

### Flexible Search
```http
POST /api/emails/search
Content-Type: application/json

{
  "search_type": "sender",
  "query": "john@example.com"
}
```

**Parameters:**
- `search_type` (string): "sender", "id", or "subject"
- `query` (string): Search term or email ID

**Response:**
```json
{
  "result": "=== Search Results ===\n..."
}
```

### API Documentation
```http
GET /api/docs
```

Returns comprehensive API documentation and endpoint information.

## Web Interface

Access the web interface at `http://localhost:5000` for interactive testing of all API endpoints.

## Testing

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Search by sender
curl "http://localhost:5000/api/emails/sender/john@example.com"

# Search by subject
curl "http://localhost:5000/api/emails/subject/meeting"

# Get email details
curl "http://localhost:5000/api/emails/id/AAMkAGI2TG93AAA="

# Flexible search
curl -X POST http://localhost:5000/api/emails/search \
  -H "Content-Type: application/json" \
  -d '{"search_type": "sender", "query": "john@example.com"}'
```

### Using Python

```python
import requests

# Search by sender
response = requests.get("http://localhost:5000/api/emails/sender/john@example.com")
print(response.json())

# Flexible search
payload = {"search_type": "subject", "query": "meeting"}
response = requests.post("http://localhost:5000/api/emails/search", json=payload)
print(response.json())
```

### Using the Test Script

```bash
python test_api.py
```

## Response Format

All successful responses return JSON with a "result" field containing the email data as a string.

### Success Response
```json
{
  "result": "=== Emails from john@example.com ===\n..."
}
```

### Error Response
```json
{
  "error": "ERROR: No emails found from sender: john@example.com"
}
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid parameters or missing required fields
- **404 Not Found**: Endpoint not found or email not found
- **500 Internal Server Error**: Server-side errors or API failures

### Common Error Scenarios

1. **Missing Parameters**: Returns 400 with clear error message
2. **Invalid Email ID**: Returns 500 with validation error
3. **No Results Found**: Returns 200 with empty result message
4. **Authentication Failure**: Returns 500 with authentication error
5. **API Rate Limiting**: Returns 500 with rate limit error

## Environment Variables

### Required Variables
- `CLIENT_ID`: Microsoft Graph API Client ID
- `TENANT_ID`: Microsoft Azure Tenant ID
- `CLIENT_SECRET`: Microsoft Graph API Client Secret
- `DEFAULT_USER_ID`: Default email user for API operations

### Optional Variables
- `DEBUG`: Enable debug mode (true/false)
- `API_TIMEOUT`: Request timeout in seconds

## Security

- All credentials stored in environment variables
- Microsoft Graph API authentication
- Input validation and sanitization
- Error messages don't expose sensitive information
- CORS headers for web interface

## Troubleshooting

### Common Issues

1. **Server won't start**: Check environment variables in `.env` file
2. **Authentication errors**: Verify Microsoft Graph API credentials
3. **No results found**: Check email address format and existence
4. **API timeouts**: Increase timeout settings in configuration
5. **Import errors**: Install missing dependencies

### Debug Mode

Enable debug logging by setting `DEBUG=true` in your environment variables.

### Validation

The server validates all required environment variables on startup and provides clear error messages if any are missing.

## Development

### Project Structure
```
app.py              # Main Flask application
Email_Tools/        # Email search utilities
templates/          # Web interface templates
utils/              # Utility functions
requirements.txt    # Python dependencies
.env               # Environment variables
```

### Adding New Endpoints

1. Add route in `app.py`
2. Import required functions from `Email_Tools/`
3. Add error handling
4. Update documentation
5. Test thoroughly

## License

This project is licensed under the MIT License.
