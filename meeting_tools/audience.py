import os
import requests
import json
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

def get_meeting_audience(meeting_id, headers, user_id=None):
    if user_id:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/events/{meeting_id}"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        meeting = response.json()
        return meeting.get('attendees', [])
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
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    retrieve_meeting_audience(meeting_id)

if __name__ == "__main__":
    main()
