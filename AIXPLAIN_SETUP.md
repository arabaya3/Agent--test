# AIXplain Integration Setup

## Environment Variables

Add these to your `.env` file:

```bash
# AIXplain Configuration
AIXPLAIN_API_KEY=your_aixplain_api_key_here
AIXPLAIN_MODEL_ID=your_model_id_here
# Note: You can also use TEAM_API_KEY instead of AIXPLAIN_API_KEY
```

## Installation

```bash
pip install aixplain
```

## Test Setup

```bash
python agent/core_agent.py
```

The agent is prepared for AIXplain integration but currently uses rule-based logic as the primary decision mechanism.

## Current Status

- ✅ **AIXplain SDK**: Installed and configured
- ✅ **Environment Setup**: Ready for API key and model ID
- ✅ **Fallback Logic**: Robust rule-based decision making
- ⏳ **AI Integration**: Framework ready, awaiting proper API documentation

## Next Steps

When AIXplain provides proper API documentation, the agent can be easily updated to use AI-powered decision making while maintaining the reliable fallback system.
