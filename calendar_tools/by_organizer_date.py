import os
import requests
import json
from datetime import datetime
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
    print("Calendar Organizer Date Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def search_meetings_by_organizer_date(organizer, date, headers):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return []
    
    url = f"https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"
    
    all_meetings = []
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            meetings = data.get("value", [])
            
            # Filter meetings by organizer
            filtered_meetings = []
            for meeting in meetings:
                meeting_organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "")
                if organizer.lower() in meeting_organizer.lower():
                    filtered_meetings.append(meeting)
            
            all_meetings.extend(filtered_meetings)
            
            print(f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by organizer... (Total filtered: {len(all_meetings)})")
            
            url = data.get("@odata.nextLink")
            
            if len(all_meetings) >= 5000:
                print("Warning: Reached 5000 meetings limit.")
                break
                
    except requests.exceptions.RequestException as e:
        print(f"Error searching meetings: {e}")
        return []
    
    return all_meetings

def retrieve_meetings_by_organizer_date(organizer, date):
    print("============================================================")
    print("Calendar Organizer Date Retriever")
    print("============================================================")
    print(f"Searching for meetings organized by: {organizer}")
    print(f"On date: {date}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return []
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    meetings = search_meetings_by_organizer_date(organizer, date, headers)
    
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total meetings found for organizer '{organizer}' on {date}: {len(meetings)}")
    
    if meetings:
        print("\nRetrieved Meetings:")
        print("============================================================")
        for i, meeting in enumerate(meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer_email = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))
            
            print(f"{i}. Subject: {subject}")
            print(f"   Organizer: {organizer_email}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
            print(f"   Attendees: {attendees_count}")
            print(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            print()
    else:
        print(f"No meetings found for organizer '{organizer}' on {date}.")
    
    return meetings

def main():
    print("============================================================")
    print("Calendar Organizer Date Retriever")
    print("============================================================")
    
    organizer = input("Enter organizer email address: ").strip()
    if not organizer:
        print("Error: Organizer email is required")
        return
    
    date = input("Enter date (YYYY-MM-DD): ").strip()
    if not date:
        print("Error: Date is required")
        return
    
    retrieve_meetings_by_organizer_date(organizer, date)

if __name__ == "__main__":
    main() 