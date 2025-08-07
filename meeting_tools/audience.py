import os
import requests
import json
from dotenv import load_dotenv
import msal

load_dotenv()

def get_access_token():
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    
    if not client_id or not tenant_id:
        print("Error: CLIENT_ID and TENANT_ID must be set in .env file")
        return None
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.PublicClientApplication(client_id, authority=authority)
    
    scopes = ["https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/User.Read", "https://graph.microsoft.com/Calendars.Read"]
    
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print("Error: Failed to create device flow")
        return None
    
    print("============================================================")
    print("Meeting Audience Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def get_meeting_audience(meeting_id, headers):
    url = f"https://graph.microsoft.com/v1.0/me/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        meeting = response.json()
        return meeting.get('attendees', [])
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving meeting audience: {e}")
        return []

def retrieve_meeting_audience(meeting_id):
    print("============================================================")
    print("Meeting Audience Retriever")
    print("============================================================")
    print(f"Retrieving audience for meeting ID: {meeting_id}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    attendees = get_meeting_audience(meeting_id, headers)
    if attendees:
        print(f"\nAudience (Attendees) List ({len(attendees)}):")
        print("============================================================")
        for i, att in enumerate(attendees, 1):
            name = att.get('emailAddress', {}).get('name', 'Unknown')
            email = att.get('emailAddress', {}).get('address', 'Unknown')
            att_type = att.get('type', '')
            print(f"{i}. {name} <{email}> ({att_type})")
    else:
        print("No attendees found for this meeting.")
    return attendees

def main():
    print("============================================================")
    print("Meeting Audience Retriever")
    print("============================================================")
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    retrieve_meeting_audience(meeting_id)

if __name__ == "__main__":
    main()
