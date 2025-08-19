import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_access_token() -> str:
    tenant_id = os.getenv("TENANT_ID") or os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET")
    if not (tenant_id and client_id and client_secret):
        print("[AUTH ERROR] TENANT_ID/CLIENT_ID/CLIENT_SECRET are not set.")
        return ""

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    try:
        resp = requests.post(token_url, data=data, timeout=30)
        resp.raise_for_status()
        tok = resp.json().get("access_token", "")
        if not tok:
            print("[AUTH ERROR] No access_token in response.")
        else:
            if os.getenv("DEBUG_AUTH", "0").strip() in ("1", "true", "yes", "y"):
                roles = resp.json().get("roles") or resp.json().get("scope")
                print(f"[AUTH DEBUG] appid: {client_id} tenant: {tenant_id}")
                if roles:
                    print(f"[AUTH DEBUG] roles/scopes: {roles}")
        return tok
    except requests.exceptions.RequestException as exc:
        print(f"[AUTH ERROR] Token request failed: {exc}")
        try:
            print(resp.text)
        except Exception:
            pass
        return ""


