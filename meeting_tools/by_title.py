import os
import requests
import json
from dotenv import load_dotenv
import os
from shared.auth import get_access_token

load_dotenv()

def search_meetings_by_title(title, headers, user_id=None):
    target_user_id = user_id or os.getenv('DEFAULT_USER_ID')
    url = f"https://graph.microsoft.com/v1.0/users/{target_user_id}/events?$filter=contains(subject,'{title}')&$orderby=start/dateTime desc&$top=100"
    all_meetings = []
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            meetings = data.get("value", [])
            all_meetings.extend(meetings)
            url = data.get("@odata.nextLink")
    except requests.exceptions.RequestException as e:
        print(f"Error searching meetings: {e}")
        return []
    return all_meetings

def retrieve_meetings_by_title(title, user_id=None):
    print("============================================================")
    print("Meeting by Title Retriever")
    print("============================================================")
    print(f"Searching for meetings with title containing: '{title}'")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    meetings = search_meetings_by_title(title, headers, user_id)
    print(f"\nTotal meetings found: {len(meetings)}\n")
    if meetings:
        for i, meeting in enumerate(meetings, 1):
            print(f"{i}. Subject: {meeting.get('subject', 'No Subject')}")
            print(f"   ID: {meeting.get('id', 'No ID')}")
            print(f"   Organizer: {meeting.get('organizer', {}).get('emailAddress', {}).get('address', 'Unknown')}")
            print(f"   Start: {meeting.get('start', {}).get('dateTime', 'Unknown')}")
            print(f"   End: {meeting.get('end', {}).get('dateTime', 'Unknown')}")
            print(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            attendees = meeting.get('attendees', [])
            print(f"   Attendees ({len(attendees)}):")
            for att in attendees:
                print(f"     - {att.get('emailAddress', {}).get('address', 'Unknown')} ({att.get('type', '')})")
            print()
    else:
        print("No meetings found with the specified title.")
    return meetings

def main():
    print("============================================================")
    print("Meeting by Title Retriever")
    print("============================================================")
    title = input("Enter meeting title or keyword: ").strip()
    if not title:
        print("Error: Meeting title is required")
        return
    retrieve_meetings_by_title(title)

if __name__ == "__main__":
    main()
