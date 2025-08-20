import os
import requests
import json
from dotenv import load_dotenv
try:
    from shared.auth import get_access_token
except ImportError:
    import sys, os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    from shared.auth import get_access_token

load_dotenv()

def get_meeting_by_id(meeting_id, headers, user_id=None):
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return None
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{meeting_id}"
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
    
    # Clean the meeting ID - remove spaces and extract actual ID if it's a URL
    import re
    
    # If it's a Teams URL, extract the meeting ID
    teams_url_pattern = r'meeting_([a-zA-Z0-9%]+)'
    teams_match = re.search(teams_url_pattern, meeting_id)
    if teams_match:
        meeting_id = teams_match.group(1)
        # URL decode the meeting ID
        import urllib.parse
        meeting_id = urllib.parse.unquote(meeting_id)
    else:
        # Remove spaces and other invalid characters for direct meeting ID
        meeting_id = re.sub(r'\s+', '', meeting_id)
    
    print(f"Cleaned meeting ID: {meeting_id}")
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot fetch meeting.")
        return
    
    retrieve_meeting_by_id(meeting_id, target_user)

if __name__ == "__main__":
    main()
