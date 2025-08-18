# 🤖 AIXPLAIN ENHANCED SMART EXECUTIVE ASSISTANT

An intelligent executive assistant that retrieves and analyzes Emails, Meetings/Calendar, and OneDrive Files via Microsoft Graph, with AIXplain-powered conversational intelligence, follow-up chats, name resolution, and smart date handling.

## 🚀 Highlights

- Real-time awareness (current date/time, relative dates)
- Conversational chat with follow-ups (context memory)
- Name-based queries (use names instead of emails)
- Intelligent “last email” detection (beyond just yesterday)
- Retrieval + analysis for emails, meetings, and files
- AIXplain GPT integration with graceful rule-based fallback

## 📦 Project Structure (simplified)

```
aiXpalin-Executive-Assistant-PoC/
├── agent/
│   ├── enhanced_smart_agent.py     # Single agent file (EnhancedSmartAgent)
│   └── advanced_analyzer.py        # Deeper insights (used by enhanced agent)
├── enhanced_assistant_master.py    # Single entry point (interactive/batch/demo)
├── email_tools/                    # Email retrieval helpers
├── calendar_tools/                 # Calendar/meeting retrieval helpers
├── meeting_tools/                  # Meeting details/transcript/attendance
├── onedrive_tools/                 # OneDrive list/retrieve/upload
├── shared/                         # Auth and shared utilities
├── requirements.txt
├── env_template.txt                # Copy to .env and fill in
├── AIXPLAIN_SETUP.md               # Optional: AIXplain setup guide
├── APPLICATION_PERMISSIONS_README.md  # Microsoft Graph permissions
├── ENV_SETUP_INSTRUCTIONS.md       # Environment setup guide
└── README.md                       # This file
```

## ⚙️ Setup

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Create `.env` (copy from `env_template.txt`) and fill:
```env
# Microsoft Graph API
CLIENT_ID=your_client_id
TENANT_ID=your_tenant_id

# AIXplain (optional but recommended)
AIXPLAIN_API_KEY=your_aixplain_api_key
AIXPLAIN_MODEL_ID=gpt-4  # e.g. gpt-4, gpt-3.5-turbo, claude-3-sonnet

# Default user (for application permissions flows)
DEFAULT_USER_ID=executive.assistant@menadevs.io
```

3) Grant Microsoft Graph permissions (see `APPLICATION_PERMISSIONS_README.md`)

## ▶️ Run

Interactive assistant (chat + retrieval + analysis):
```bash
python enhanced_assistant_master.py
```

Useful commands inside interactive mode:
- `help` shows examples
- `time` shows current date/time
- `user` switches the target user ID
- `quit` exits

## 💬 Example Queries

Email:
- "emails from John"
- "last email"
- "recent emails"
- "who sent the most emails last week"

Meetings:
- "meetings this week"
- "meetings with Mike"
- "who organized the most meetings last month"

Files:
- "list files in Documents folder"
- "recent files"
- "large files"

Follow-ups:
- After: "emails from John" → "what about Sarah?"
- "and Mike too"
- "also show me recent files"

## 🧠 How it Works (brief)

- Single agent: `agent/enhanced_smart_agent.py` (EnhancedSmartAgent)
  - AIXplain model for intent + rule-based fallback
  - Real-time date parsing and smart “last email” ranges
  - NameResolver to map names → emails
  - Conversation memory for follow-ups
  - AdvancedAnalyzer for natural-language insights

## 🔐 Notes

- Ensure Azure AD app has required Graph permissions (Mail.Read, Calendars.Read, Files.Read, etc.)
- AIXplain is optional; the agent falls back to rules if not configured

## 📄 License

MIT License – see `LICENSE`
