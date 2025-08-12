import os
import requests
from dotenv import load_dotenv
import msal

load_dotenv()

def get_access_token():
    """
    Get access token using application permissions (client credentials flow)
    instead of delegated permissions (device flow)
    """
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not client_id or not tenant_id or not client_secret:
        print("Error: CLIENT_ID, TENANT_ID, and CLIENT_SECRET must be set in .env file")
        return None
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
    # Use ConfidentialClientApplication for application permissions
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority
    )
    
    # Use client credentials flow for application permissions
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        print(f"Error code: {result.get('error', 'Unknown')}")
        return None
