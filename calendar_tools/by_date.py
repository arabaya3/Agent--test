import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

def search_meetings_by_date(date, headers, user_id=None):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return []
    
    filter_query = f"start/dateTime ge '{start_datetime}' and start/dateTime le '{end_datetime}'"
    
    if user_id:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"
    
    all_meetings = []
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            meetings = data.get("value", [])
            all_meetings.extend(meetings)
            
            print(f"Retrieved {len(meetings)} meetings... (Total: {len(all_meetings)})")
            
            url = data.get("@odata.nextLink")
            
            if len(all_meetings) >= 5000:
                print("Warning: Reached 5000 meetings limit.")
                break
                
    except requests.exceptions.RequestException as e:
        print(f"Error searching meetings: {e}")
        return []
    
    return all_meetings

def retrieve_meetings_by_date(date, user_id=None):
    print("============================================================")
    print("Calendar Date Retriever")
    print("============================================================")
    print(f"Searching for meetings on: {date}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    meetings = search_meetings_by_date(date, headers, user_id)
    
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total meetings found: {len(meetings)}")
    
    if meetings:
        print("\nRetrieved Meetings:")
        print("============================================================")
        for i, meeting in enumerate(meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))
            
            print(f"{i}. Subject: {subject}")
            print(f"   Organizer: {organizer}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
            print(f"   Attendees: {attendees_count}")
            print(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            print()
    else:
        print("No meetings found for the specified date.")
    
    return meetings

def main():
    print("============================================================")
    print("Calendar Date Retriever")
    print("============================================================")
    
    date = input("Enter date (YYYY-MM-DD): ").strip()
    if not date:
        print("Error: Date is required")
        return
    
    retrieve_meetings_by_date(date)

if __name__ == "__main__":
    main() 