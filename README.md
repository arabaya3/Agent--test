# Core Assistant Pipeline - AIXPLAIN Smart Agent System

## 🎯 Overview

The Core Assistant Pipeline is a sophisticated Microsoft 365 integration system powered by **AIXPLAIN Smart Agents**. It provides intelligent, context-aware assistance for managing emails, meetings, calendar events, and OneDrive files through natural language queries.

## 🧠 AIXPLAIN Smart Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER AGENT                             │
│              (Query Classification & Routing)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│EMAIL  │   │CALENDAR │   │ONEDRIVE │
│AGENT  │   │ AGENT   │   │ AGENT   │
└───────┘   └─────────┘   └─────────┘
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│MEETING│   │AIXPLAIN │   │AIXPLAIN │
│AGENT  │   │ANALYSIS │   │ANALYSIS │
└───────┘   └─────────┘   └─────────┘
```

### Specialized Agents

- **📧 Email Agent**: Intelligent email processing with pattern analysis
- **📅 Calendar Agent**: Smart calendar management and scheduling insights
- **📁 OneDrive Agent**: Advanced file management with AI-powered filtering
- **🎯 Meeting Agent**: Comprehensive meeting analysis and transcript processing

## 🚀 Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd Core-Assistant-Pipeline
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:

```bash
# AIXPLAIN Configuration
AIXPLAIN_API_KEY=your_aixplain_api_key_here
AIXPLAIN_MODEL_ID=your_model_id_here
TEAM_API_KEY=your_team_api_key_here

# Microsoft Graph
CLIENT_ID=your_client_id
TENANT_ID=your_tenant_id
CLIENT_SECRET=your_client_secret
DEFAULT_USER_ID=executive.assistant@menadevs.io
```

### 3. Get AIXPLAIN Credentials

1. Sign up at [https://aixplain.com](https://aixplain.com)
2. Create an API key in your dashboard
3. Select a model (recommended: GPT-4 or Claude)
4. Get your Team API key for advanced features

### 4. Run the System

```bash
# Interactive mode
python enhanced_assistant_master.py

# Demo mode
python enhanced_assistant_master.py demo

# Batch mode
python enhanced_assistant_master.py batch "emails from today" "meetings this week"
```

## 🎯 Capabilities

### Email Management
- **Smart Query Understanding**: "Show me urgent emails from yesterday"
- **Sender Analysis**: "Find emails from mohammad.mowas@menadevs.io"
- **Pattern Recognition**: "Analyze my email patterns from last week"
- **Attachment Filtering**: "Get emails with attachments"

### Calendar & Meetings
- **Meeting Retrieval**: "What meetings do I have today?"
- **Organizer Filtering**: "Show meetings organized by John"
- **Transcript Access**: "Get transcript for yesterday's meeting"
- **Attendance Tracking**: "Who attended the project meeting?"

### File Management
- **Intelligent Listing**: "List my OneDrive files"
- **Type Filtering**: "Show me PDF documents"
- **Size Analysis**: "Find files larger than 10MB"
- **Storage Insights**: "Analyze my file storage"

### Multi-Domain Queries
- **Cross-Reference**: "Show me emails about meetings from today"
- **Summary Requests**: "Give me a summary of my week"
- **Pattern Analysis**: "What are my most frequent activities?"

## 📁 Project Structure

```
Core-Assistant-Pipeline/
├── agents/                          # AIXPLAIN Smart Agents
│   ├── __init__.py
│   ├── master_agent.py             # Orchestrator agent
│   ├── email_agent.py              # Email specialist
│   ├── calendar_agent.py           # Calendar specialist
│   ├── onedrive_agent.py           # File specialist
│   └── meeting_agent.py            # Meeting specialist
├── email_tools/                     # Email processing tools
├── calendar_tools/                  # Calendar processing tools
├── meeting_tools/                   # Meeting processing tools
├── onedrive_tools/                  # File processing tools
├── shared/                          # Shared utilities
├── enhanced_assistant_master.py     # Main application
├── AIXPLAIN_SETUP.md               # Detailed setup guide
└── requirements.txt                 # Dependencies
```

## 🔧 Configuration

### AIXPLAIN Models

| Model | Use Case | Performance | Cost |
|-------|----------|-------------|------|
| `gpt-4` | Complex analysis, multi-agent coordination | High | High |
| `gpt-3.5-turbo` | General queries, good balance | Medium | Medium |
| `claude-3-sonnet` | Detailed analysis, document processing | High | Medium |
| `claude-3-haiku` | Fast responses, simple queries | Fast | Low |

### Environment Variables

```bash
# Required for AIXPLAIN functionality
AIXPLAIN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AIXPLAIN_MODEL_ID=gpt-4
TEAM_API_KEY=team_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Required for Microsoft Graph
CLIENT_ID=your_client_id
TENANT_ID=your_tenant_id
CLIENT_SECRET=your_client_secret
DEFAULT_USER_ID=executive.assistant@menadevs.io
```

## 🧪 Testing

### Basic Functionality Test

```bash
python enhanced_assistant_master.py
```

Try these queries:
- "hello"
- "emails from today"
- "meetings this week"
- "list my files"

### AIXPLAIN Integration Test

```bash
# Test with complex queries that require AI analysis
"Analyze my email patterns from last week"
"Summarize my meeting schedule"
"Find important documents in my OneDrive"
```

### Batch Testing

```bash
python enhanced_assistant_master.py batch "emails from today" "meetings this week" "list files"
```

## 🚨 Troubleshooting

### Common Issues

1. **AIXPLAIN Import Error**
   ```bash
   pip install aixplain==0.2.33
   ```

2. **Authentication Failed**
   - Check your API keys in `.env` file
   - Verify AIXPLAIN credentials

3. **Fallback Mode Active**
   - Check AIXPLAIN credentials and internet connection
   - System will work with rule-based fallback

### Debug Mode

```bash
export DEBUG=1
python enhanced_assistant_master.py
```

## 📊 Performance Features

- **Intelligent Caching**: Email IDs and meeting data cached for faster retrieval
- **Batch Processing**: Efficient handling of multiple queries
- **Fallback System**: Graceful degradation when AIXPLAIN is unavailable
- **Parallel Processing**: Multi-agent coordination for complex queries

## 🔐 Security

- **API Key Protection**: Environment variables for sensitive data
- **Data Privacy**: AIXPLAIN processes data according to privacy policy
- **Access Control**: Application permissions for Microsoft Graph
- **No Data Storage**: All processing done in-memory

## 📈 Advanced Features

### Custom Prompts
Customize AIXPLAIN prompts in each agent for specific use cases.

### Multi-Agent Coordination
The master agent coordinates multiple agents for complex queries.

### Custom Analysis
Add custom analysis functions to each agent.

## 📞 Support

- **AIXPLAIN Issues**: [support@aixplain.com](mailto:support@aixplain.com)
- **Microsoft Graph**: [Microsoft Graph documentation](https://docs.microsoft.com/graph)
- **System Issues**: Check troubleshooting section in `AIXPLAIN_SETUP.md`

## 🎉 Success Indicators

Your system is working correctly when you see:

1. ✅ "AIXPLAIN Smart Agent System initialized"
2. ✅ "Email Agent AIXPLAIN initialized"
3. ✅ "Calendar Agent AIXPLAIN initialized"
4. ✅ "OneDrive Agent AIXPLAIN initialized"
5. ✅ "Meeting Agent AIXPLAIN initialized"
6. ✅ Complex queries return AIXPLAIN analysis
7. ✅ Natural language responses are intelligent and contextual

## 🚀 Next Steps

1. **Customize Prompts**: Adapt AIXPLAIN prompts for your specific use cases
2. **Add New Agents**: Create specialized agents for other data sources
3. **Integrate with Web UI**: Build a web interface for the agent system
4. **Add Analytics**: Track query patterns and system performance
5. **Scale Up**: Deploy to production with proper monitoring

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Powered by AIXPLAIN SDK v0.2.33** 🎯
