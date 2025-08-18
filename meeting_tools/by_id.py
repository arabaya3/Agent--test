import os
import requests
import json
from dotenv import load_dotenv
import os
from shared.auth import get_access_token

load_dotenv()

def get_meeting_by_id(meeting_id, headers, user_id=None):
    target_user_id = user_id or os.getenv('DEFAULT_USER_ID')
    url = f"https://graph.microsoft.com/v1.0/users/{target_user_id}/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving meeting {meeting_id}: {e}")
        return None

def retrieve_meeting_by_id(meeting_id, user_id=None):
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
    
    meeting = get_meeting_by_id(meeting_id, headers, user_id)
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
