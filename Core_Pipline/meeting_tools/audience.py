import os
import requests
import json
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import shared modules
try:
    from shared.auth import get_access_token
except ImportError:
    # If running directly, add the parent directory to the path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from shared.auth import get_access_token

load_dotenv()

def get_meeting_audience(meeting_id, headers, user_id=None):
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return []
    
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            meeting = response.json()
            return meeting.get('attendees', [])
        elif response.status_code == 404:
            print("Meeting not found. The meeting ID might be invalid or the meeting has been deleted.")
            return []
        elif response.status_code == 400:
            print(f"Bad request error: {response.status_code}")
            print(f"Response: {response.text}")
            print("This might be due to an invalid meeting ID format.")
            return []
        else:
            print(f"Error getting meeting details: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving meeting audience: {e}")
        return []

def retrieve_meeting_audience(meeting_id, user_id=None):
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
    
    attendees = get_meeting_audience(meeting_id, headers, user_id)
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
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot fetch meeting audience.")
        return
    
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    
    retrieve_meeting_audience(meeting_id, target_user)

if __name__ == "__main__":
    main()
