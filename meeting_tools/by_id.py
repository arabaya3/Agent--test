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
    print("Meeting by ID Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def get_meeting_by_id(meeting_id, headers):
    url = f"https://graph.microsoft.com/v1.0/me/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving meeting {meeting_id}: {e}")
        return None

def retrieve_meeting_by_id(meeting_id):
    print("============================================================")
    print("Meeting by ID Retriever")
    print("============================================================")
    print(f"Retrieving meeting with ID: {meeting_id}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    meeting = get_meeting_by_id(meeting_id, headers)
    if meeting:
        print("\nMeeting Details:")
        print("============================================================")
        print(f"Subject: {meeting.get('subject', 'No Subject')}")
        print(f"Organizer: {meeting.get('organizer', {}).get('emailAddress', {}).get('address', 'Unknown')}")
        print(f"Start: {meeting.get('start', {}).get('dateTime', 'Unknown')}")
        print(f"End: {meeting.get('end', {}).get('dateTime', 'Unknown')}")
        print(f"Location: {meeting.get('location', {}).get('displayName', 'No location')}")
        attendees = meeting.get('attendees', [])
        print(f"Attendees ({len(attendees)}):")
        for att in attendees:
            print(f"  - {att.get('emailAddress', {}).get('address', 'Unknown')} ({att.get('type', '')})")
    else:
        print("No meeting found with the specified ID.")
    return meeting

def main():
    print("============================================================")
    print("Meeting by ID Retriever")
    print("============================================================")
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    retrieve_meeting_by_id(meeting_id)

if __name__ == "__main__":
    main()
