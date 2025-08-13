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
```

## How to Create the .env File

1. In the root directory of this project, create a new file named `.env`
2. Copy and paste the content above
3. Replace the placeholder values with your actual Azure app registration details
4. Save the file

## Customizing the Default User ID

If you want to use a different user ID instead of `executive.assistant@menadevs.io`, simply change the `DEFAULT_USER_ID` value in your `.env` file:

```bash
DEFAULT_USER_ID=your_preferred_email@domain.com
```

## Security Note

The `.env` file is already included in `.gitignore`, so it won't be committed to version control. Keep your client secret secure and never share it publicly.
