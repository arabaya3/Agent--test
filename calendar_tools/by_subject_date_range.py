import os
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

def search_meetings_by_subject_date_range(subject, start_date, end_date, headers, user_id=None):
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return []
    
    target_user_id = user_id or os.getenv('DEFAULT_USER_ID')
    url = f"https://graph.microsoft.com/v1.0/users/{target_user_id}/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"
    
    all_meetings = []
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            meetings = data.get("value", [])
            
                                        
            filtered_meetings = []
            for meeting in meetings:
                meeting_subject = meeting.get("subject", "")
                if subject.lower() in meeting_subject.lower():
                    filtered_meetings.append(meeting)
            
            all_meetings.extend(filtered_meetings)
            
            print(f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by subject... (Total filtered: {len(all_meetings)})")
            
            url = data.get("@odata.nextLink")
            
            if len(all_meetings) >= 5000:
                print("Warning: Reached 5000 meetings limit. Consider narrowing your search criteria.")
                break
                
    except requests.exceptions.RequestException as e:
        print(f"Error searching meetings: {e}")
        return []
    
    return all_meetings

def retrieve_meetings_by_subject_date_range(subject, start_date, end_date, user_id=None):
    print("============================================================")
    print("Calendar Subject Date Range Retriever")
    print("============================================================")
    print(f"Searching for meetings with subject containing: '{subject}'")
    print(f"From: {start_date}")
    print(f"To: {end_date}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    meetings = search_meetings_by_subject_date_range(subject, start_date, end_date, headers, user_id)
    
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total meetings found with subject '{subject}' from {start_date} to {end_date}: {len(meetings)}")
    
    if meetings:
        print("\nRetrieved Meetings:")
        print("============================================================")
        for i, meeting in enumerate(meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            meeting_subject = meeting.get("subject", "No Subject")
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))
            
            print(f"{i}. Subject: {meeting_subject}")
            print(f"   Organizer: {organizer}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
            print(f"   Attendees: {attendees_count}")
            print(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            print()
    else:
        print(f"No meetings found with subject '{subject}' in the specified date range.")
    
    return meetings

def main():
    print("============================================================")
    print("Calendar Subject Date Range Retriever")
    print("============================================================")
    
    subject = input("Enter subject keyword to search: ").strip()
    if not subject:
        print("Error: Subject keyword is required")
        return
    
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if not start_date:
        print("Error: Start date is required")
        return
    
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    if not end_date:
        print("Error: End date is required")
        return
    
    retrieve_meetings_by_subject_date_range(subject, start_date, end_date)

if __name__ == "__main__":
    main() 