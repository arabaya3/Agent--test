# 🎯 AIXPLAIN Email Agent Setup Guide

## 📋 Overview

This guide will help you set up an AIXPLAIN Email Agent that integrates with your existing Core Assistant Pipeline. The Email Agent will use AIXPLAIN's platform to provide intelligent email management and analysis capabilities.

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

Create or update your `.env` file:

```bash
# AIXPLAIN Configuration
AIXPLAIN_API_KEY=your_aixplain_api_key_here
TEAM_API_KEY=your_team_api_key_here

# Microsoft Graph (existing)
CLIENT_ID=your_client_id
TENANT_ID=your_tenant_id
CLIENT_SECRET=your_client_secret
DEFAULT_USER_ID=executive.assistant@menadevs.io

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Get AIXPLAIN Credentials

1. **Sign up at AIXPLAIN**: Visit [https://aixplain.com](https://aixplain.com)
2. **Create API Key**: Go to your dashboard and create an API key
3. **Get Team API Key**: For advanced features, get your Team API key
4. **Add to .env**: Update your `.env` file with the API keys

### Step 4: Start the API Server

```bash
# Start the FastAPI server that exposes your email tools
python api_server.py
```

The server will start on `http://localhost:8000` and provide these endpoints:
- `POST /email/by-date-range`
- `POST /email/by-sender-date`
- `POST /email/by-subject-date-range`
- `POST /email/by-ids`
- `GET /email/cached-ids`
- `POST /email/refresh-cache`

### Step 5: Create the Email Agent

```bash
# Run the Email Agent setup script
python email_agent_setup.py
```

This will:
1. Create the Email Agent on AIXPLAIN platform
2. Add web tools that connect to your API server
3. Test the agent with sample queries
4. Deploy the agent for production use
5. Save agent information to `email_agent_info.json`

### Step 6: Test the Integration

```bash
# Test the Email Agent integration
python email_agent_client.py
```

## 📁 File Structure

```
Core-Assistant-Pipeline/
├── email_agent_setup.py          # AIXPLAIN Email Agent setup script
├── api_server.py                 # FastAPI server for email tools
├── email_agent_client.py         # Email Agent integration client
├── email_agent_info.json         # Generated agent information
├── email_tools/                  # Existing email tools
├── calendar_tools/               # Existing calendar tools
├── meeting_tools/                # Existing meeting tools
├── onedrive_tools/               # Existing OneDrive tools
├── shared/                       # Shared utilities
├── enhanced_assistant_master.py  # Main application
└── requirements.txt              # Dependencies
```

## 🔧 Configuration Details

### AIXPLAIN Model Configuration

The Email Agent uses:
- **Model**: GPT-4 (`669a63646eb56306647e1091`)
- **Temperature**: 0.1 (for consistent email processing)
- **Max Tokens**: 2000 (for detailed email analysis)
- **Top P**: 0.9 (for focused responses)

### Email Agent Instructions

The agent is configured with comprehensive instructions for:
- Email retrieval by date range
- Email filtering by sender and date
- Email search by subject and date range
- Email retrieval by specific IDs
- Email pattern analysis
- Date parsing (today, yesterday, last week, etc.)

### Web Tools Configuration

The Email Agent has 4 web tools connected to your API:

1. **email_by_date_range**: Retrieve emails within date range
2. **email_by_sender_date**: Find emails from specific sender on date
3. **email_by_subject_date_range**: Search emails by subject keyword
4. **email_by_ids**: Retrieve specific emails by IDs

## 🧪 Testing

### Test the API Server

```bash
# Test API endpoints
curl -X POST "http://localhost:8000/email/by-date-range" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

### Test the Email Agent

```bash
# Test with natural language queries
python email_agent_client.py
```

Sample queries to test:
- "Show me emails from yesterday"
- "Find emails from john@company.com today"
- "Search for urgent emails from last week"
- "Analyze my email patterns from this week"

## 🔗 Integration with Main Application

### Option 1: Direct Integration

Update your `enhanced_assistant_master.py` to use the Email Agent:

```python
from email_agent_client import EmailAgentIntegration

class EnhancedAssistantMaster:
    def __init__(self):
        # ... existing initialization ...
        self.email_agent = EmailAgentIntegration()
    
    def process_email_query(self, query: str):
        return self.email_agent.process_email_query(query)
```

### Option 2: API Integration

Use the Email Agent via API calls:

```python
import requests

def query_email_agent(query: str, agent_id: str, api_key: str):
    url = f"https://platform-api.aixplain.com/sdk/agents/{agent_id}/run"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    data = {"query": query}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

## 📊 Monitoring and Debugging

### Check Agent Status

```bash
# Get agent information
curl -X GET "https://platform-api.aixplain.com/sdk/agents/{AGENT_ID}" \
  -H "x-api-key: YOUR_API_KEY"
```

### View Agent Dashboard

Visit: `https://platform.aixplain.com/discover/agent/{AGENT_ID}`

### Check API Server Logs

The FastAPI server provides detailed logs for debugging:
- Request/response logs
- Error details
- Performance metrics

## 🚨 Troubleshooting

### Common Issues

1. **AIXPLAIN Import Error**
   ```bash
   pip install aixplain==0.2.33
   ```

2. **API Key Issues**
   - Verify `AIXPLAIN_API_KEY` in `.env`
   - Check API key permissions
   - Ensure Team API key is set

3. **API Server Connection**
   - Ensure API server is running on port 8000
   - Check firewall settings
   - Verify API endpoints are accessible

4. **Tool Connection Errors**
   - Verify API server is running
   - Check tool URLs in agent configuration
   - Ensure proper request/response schemas

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
python email_agent_setup.py
```

## 📈 Performance Optimization

### Agent Performance

- **Model Selection**: GPT-4 provides best quality, GPT-3.5-turbo for cost optimization
- **Temperature**: Keep at 0.1 for consistent email processing
- **Max Tokens**: Adjust based on expected email content length

### API Server Performance

- **Caching**: Email IDs are cached for faster retrieval
- **Connection Pooling**: FastAPI handles concurrent requests efficiently
- **Error Handling**: Graceful fallback for failed requests

## 🔐 Security Considerations

1. **API Key Protection**: Store keys in environment variables
2. **HTTPS**: Use HTTPS in production for API server
3. **Authentication**: Implement proper authentication for API endpoints
4. **Rate Limiting**: Consider rate limiting for API calls

## 🎯 Next Steps

After setting up the Email Agent:

1. **Create Other Agents**: Calendar, Meeting, OneDrive agents
2. **Build Orchestrator**: Master agent to coordinate all agents
3. **Add Web Interface**: Build a web UI for the agent system
4. **Production Deployment**: Deploy to production with monitoring
5. **Custom Analysis**: Add custom email analysis features

## 📞 Support

- **AIXPLAIN Issues**: [support@aixplain.com](mailto:support@aixplain.com)
- **API Documentation**: [https://docs.aixplain.com](https://docs.aixplain.com)
- **System Issues**: Check troubleshooting section above

## 🎉 Success Indicators

Your Email Agent is working correctly when you see:

1. ✅ "Email Agent created successfully"
2. ✅ "Added 4 tools to Email Agent"
3. ✅ "Email Agent deployed successfully"
4. ✅ Natural language queries return intelligent responses
5. ✅ API server responds to tool calls
6. ✅ Integration tests pass

---

**Powered by AIXPLAIN SDK v0.2.33** 🎯
