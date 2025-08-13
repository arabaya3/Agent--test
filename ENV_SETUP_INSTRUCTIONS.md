# Environment Setup Instructions

## .env File Configuration

Create a `.env` file in the root directory of this project with the following content:

```bash
# Microsoft Graph API Configuration for Application Permissions
CLIENT_ID=your_client_id_here
TENANT_ID=your_tenant_id_here
CLIENT_SECRET=your_client_secret_here

# Default User ID for Application Permissions
DEFAULT_USER_ID=executive.assistant@menadevs.io

# AIXplain Configuration (for intelligent query routing)
AIXPLAIN_API_KEY=your_aixplain_api_key_here
AIXPLAIN_MODEL_ID=your_model_id_here
# Note: AIXPLAIN_API_KEY can also be set as TEAM_API_KEY
```

## How to Create the .env File

1. In the root directory of this project, create a new file named `.env`
2. Copy and paste the content above
3. Replace the placeholder values with your actual Azure app registration details
4. For AIXplain, get your API key from [AIXplain Platform](https://platform.aixplain.com/)
5. Choose any text generation model ID (e.g., gpt-4, claude-3-sonnet)
6. Save the file

## Customizing the Default User ID

If you want to use a different user ID instead of `executive.assistant@menadevs.io`, simply change the `DEFAULT_USER_ID` value in your `.env` file:

```bash
DEFAULT_USER_ID=your_preferred_email@domain.com
```

## Security Note

The `.env` file is already included in `.gitignore`, so it won't be committed to version control. Keep your client secret and API keys secure and never share them publicly.

## AIXplain Integration

The system now uses AIXplain models for intelligent query routing. If AIXplain is not configured, the system will automatically fall back to rule-based logic. This ensures the application works even without AIXplain setup.
