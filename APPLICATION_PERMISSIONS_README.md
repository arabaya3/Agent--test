# Application Permissions Migration Guide

This document explains the changes made to migrate from delegated permissions to application permissions in the Core Assistant Pipeline.

## What Changed

### 1. Authentication Method
- **Before**: Used delegated permissions with device flow authentication (`msal.PublicClientApplication`)
- **After**: Uses application permissions with client credentials flow (`msal.ConfidentialClientApplication`)

### 2. API Endpoints
- **Before**: Used `/me/*` endpoints (user-specific)
- **After**: Uses `/users/{user-id}/*` endpoints (application can access any user's data)

### 3. Function Signatures
- **Before**: Functions like `retrieve_emails_by_date_range(date, headers, email_ids)`
- **After**: Functions now accept `user_id` parameter: `retrieve_emails_by_date_range(date, headers, email_ids, user_id)`

### 4. Required Environment Variables
You need to set these environment variables in your `.env` file:

```bash
# Microsoft Graph API Configuration for Application Permissions
CLIENT_ID=your_client_id_here
TENANT_ID=your_tenant_id_here
CLIENT_SECRET=your_client_secret_here
DEFAULT_USER_ID=executive.assistant@menadevs.io
```

## How to Use

### 1. Set Up Environment Variables
Create a `.env` file in the root directory with your Azure app registration details:

```bash
CLIENT_ID=12345678-1234-1234-1234-123456789012
TENANT_ID=87654321-4321-4321-4321-210987654321
CLIENT_SECRET=your_client_secret_value_here
DEFAULT_USER_ID=executive.assistant@menadevs.io
```

### 2. Grant Admin Consent
In Azure Portal, make sure to:
1. Go to your app registration
2. Navigate to "API permissions"
3. Click "Grant admin consent for [Your Organization]"
4. Ensure all required permissions show "Granted for [Your Organization]"

### 3. Run the Application
The application automatically uses `executive.assistant@menadevs.io` as the default user ID for all operations, eliminating the need to manually enter a user ID each time.

### 4. User ID Configuration
- **Default User ID**: `executive.assistant@menadevs.io` (can be configured in `.env` file via `DEFAULT_USER_ID`)
- **Email operations (1-4)**: Uses default user ID automatically
- **Calendar operations (5-8)**: Uses default user ID automatically  
- **Meeting operations (9-13)**: Uses default user ID automatically
- **Customization**: To use a different user ID, add `DEFAULT_USER_ID=your_email@domain.com` to your `.env` file

## Required Permissions

Based on the Azure portal screenshot, ensure your app has these **Application** permissions:

### Calendar Permissions
- `Calendars.Read.All` - Read calendars in all mailboxes
- `Calendars.ReadWrite.All` - Read and write calendars in all mailboxes

### Email Permissions
- `Mail.Read.All` - Read mail in all mailboxes
- `Mail.ReadWrite.All` - Read and write mail in all mailboxes

### Meeting Permissions
- `CallTranscripts.Read.All` - Read all call transcripts
- `OnlineMeetings.Read.All` - Read all online meetings

## Benefits of Application Permissions

1. **No User Interaction Required**: No need for device flow or user consent
2. **Background Processing**: Can run automated scripts and services
3. **Multi-User Access**: Can access data for any user in the organization
4. **Higher Rate Limits**: Generally higher API call limits

## Security Considerations

1. **Admin Consent Required**: Application permissions require admin consent
2. **Broad Access**: The app can access any user's data within the organization
3. **Client Secret Management**: Store client secrets securely and rotate regularly
4. **Principle of Least Privilege**: Only grant the minimum permissions needed

## Troubleshooting

### Common Issues

1. **"Insufficient privileges" error**
   - Ensure admin consent has been granted
   - Check that the correct permission types (Application vs Delegated) are configured

2. **"Invalid client" error**
   - Verify CLIENT_ID and CLIENT_SECRET are correct
   - Ensure the client secret hasn't expired

3. **"User not found" error**
   - Verify the user ID/email exists in your organization
   - Check that the app has permissions to access user data

### Testing

To test the setup:
1. Run the main application: `python assistant_retriever_master.py`
2. Choose any email option (1-4)
3. Enter a valid user ID or email address
4. The application should authenticate without prompting for device flow

## Migration Notes

- All existing functionality has been preserved
- The API endpoints now require user ID specification
- Authentication is now completely automated
- No more device flow prompts or user interaction required
- All tools (email, calendar, meeting) now support application permissions
- User ID is required for all operations to specify which user's data to access

## Updated Tools

### Email Tools ✅
- `by_id.py` - Retrieve emails by ID list
- `by_sender_date.py` - Retrieve emails by sender and date
- `by_date_range.py` - Retrieve emails by date range
- `by_subject_date_range.py` - Retrieve emails by subject and date range

### Email Retrieval Improvements ✅
- **No Duplicate Emails**: Implemented conversation-level deduplication to prevent duplicate emails
- **Always Include Main Email**: Removed user prompts - main email and all replies are always included
- **Conversation Threading**: Each email retrieval now includes the complete conversation thread
- **Automatic Deduplication**: Uses email ID-based deduplication within conversations
- **Global Deduplication**: Prevents processing the same conversation multiple times across search results
- **Accurate Reporting**: Shows both total emails found and unique conversations processed

### Calendar Tools ✅
- `by_date.py` - Get meetings by date
- `by_organizer_date.py` - Retrieve meetings by organizer and date
- `by_date_range.py` - Retrieve all meetings within date range
- `by_subject_date_range.py` - Retrieve meetings by subject and date range

### Meeting Tools ✅
- `by_id.py` - Get meeting by ID
- `by_title.py` - Get meeting by title
- `transcript.py` - Get transcript from meeting ID
- `audience.py` - Get audience (attendees) from meeting ID
- `attendance.py` - Get attendance from meeting ID
