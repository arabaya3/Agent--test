import os
import requests
from dotenv import load_dotenv
import msal
import json as _json
import base64 as _base64

load_dotenv()

def get_access_token():
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not client_id or not tenant_id or not client_secret:
        print("Error: CLIENT_ID, TENANT_ID, and CLIENT_SECRET must be set in .env file")
        return None
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
                                                                   
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority
    )
    
                                                             
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" in result:
        token = result["access_token"]
                                                                        
        if os.getenv("DEBUG_AUTH", "0") == "1":
            try:
                                                                              
                parts = token.split(".")
                if len(parts) >= 2:
                    padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
                    payload_bytes = _base64.urlsafe_b64decode(padded)
                    claims = _json.loads(payload_bytes.decode("utf-8"))
                    roles = claims.get("roles") or claims.get("scp")
                    appid = claims.get("appid")
                    tid = claims.get("tid")
                    print("[AUTH DEBUG] appid:", appid, "tenant:", tid)
                    print("[AUTH DEBUG] roles/scopes:", roles)
            except Exception as _:
                pass
        return token
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        print(f"Error code: {result.get('error', 'Unknown')}")
        return None
