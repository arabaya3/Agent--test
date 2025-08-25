import os
import requests
import json
import sys
from datetime import datetime
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_access_token():
    """Get access token for Microsoft Graph API"""
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        return None
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        response = requests.post(token_url, data=token_data,
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            return None
    except:
        return None

def search_meetings_by_organizer_date(organizer: str, date: str, user_id: Optional[str] = None) -> str:
    """
    Search meetings by organizer and date
    
    Args:
        organizer: Organizer email address
        date: Date in YYYY-MM-DD format
        user_id: Optional user ID to search for
    
    Returns:
        Formatted string with meeting details or error message
    """
    lines = []
    
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format"

    if not user_id:
        user_id = os.getenv("GRAPH_USERNAME") or os.getenv("DEFAULT_USER_ID")
        if not user_id:
            return "Error: DEFAULT_USER_ID not set in environment variables"

    access_token = get_access_token()
    if not access_token:
        return "Error: Unable to obtain access token"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

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

            filtered_meetings = []
            for meeting in meetings:
                meeting_organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "")
                if organizer.lower() in meeting_organizer.lower():
                    filtered_meetings.append(meeting)

            all_meetings.extend(filtered_meetings)

            lines.append(
                f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by organizer... (Total filtered: {len(all_meetings)})"
            )

            url = data.get("@odata.nextLink")

            if len(all_meetings) >= 5000:
                lines.append("Warning: Reached 5000 meetings limit.")
                break

    except requests.exceptions.RequestException as e:
        return f"Error searching meetings: {e}"

    lines.append("============================================================")
    lines.append("Calendar Organizer Date Retriever")
    lines.append("============================================================")
    lines.append(f"Total meetings found for organizer '{organizer}' on {date}: {len(all_meetings)}")

    if all_meetings:
        lines.append("")
        lines.append("Retrieved Meetings:")
        lines.append("============================================================")
        for i, meeting in enumerate(all_meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer_email = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            lines.append(f"{i}. Subject: {subject}")
            lines.append(f"   ID: {meeting.get('id', 'Unknown')}")
            lines.append(f"   Organizer: {organizer_email}")
            lines.append(f"   Start: {start_time}")
            lines.append(f"   End: {end_time}")
            lines.append(f"   Attendees: {attendees_count}")
            lines.append(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            lines.append("")
    else:
        lines.append(f"No meetings found for organizer '{organizer}' on {date}.")

    return "\n".join(lines)

def search_meetings_by_subject_date_range(subject: str, start_date: str, end_date: str, user_id: Optional[str] = None) -> str:
    """
    Search meetings by subject and date range
    
    Args:
        subject: Subject keyword to search for
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_id: Optional user ID to search for
    
    Returns:
        Formatted string with meeting details or error message
    """
    lines = []
    
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")

        start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        return "Error: Dates must be in YYYY-MM-DD format"

    if not user_id:
        user_id = os.getenv("GRAPH_USERNAME") or os.getenv("DEFAULT_USER_ID")
        if not user_id:
            return "Error: DEFAULT_USER_ID not set in environment variables"

    access_token = get_access_token()
    if not access_token:
        return "Error: Unable to obtain access token"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

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

            filtered_meetings = []
            for meeting in meetings:
                meeting_subject = meeting.get("subject", "")
                if subject.lower() in meeting_subject.lower():
                    filtered_meetings.append(meeting)

            all_meetings.extend(filtered_meetings)

            lines.append(
                f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by subject... (Total filtered: {len(all_meetings)})"
            )

            url = data.get("@odata.nextLink")

            if len(all_meetings) >= 5000:
                lines.append("Warning: Reached 5000 meetings limit. Consider narrowing your search criteria.")
                break

    except requests.exceptions.RequestException as e:
        return f"Error searching meetings: {e}"

    lines.append("============================================================")
    lines.append("Calendar Subject Date Range Retriever")
    lines.append("============================================================")
    lines.append(f"Total meetings found with subject '{subject}' from {start_date} to {end_date}: {len(all_meetings)}")

    if all_meetings:
        lines.append("")
        lines.append("Retrieved Meetings:")
        lines.append("============================================================")
        for i, meeting in enumerate(all_meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            meeting_subject = meeting.get("subject", "No Subject")
            organizer_email = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            lines.append(f"{i}. Subject: {meeting_subject}")
            lines.append(f"   ID: {meeting.get('id', 'Unknown')}")
            lines.append(f"   Organizer: {organizer_email}")
            lines.append(f"   Start: {start_time}")
            lines.append(f"   End: {end_time}")
            lines.append(f"   Attendees: {attendees_count}")
            lines.append(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            lines.append("")
    else:
        lines.append(f"No meetings found with subject '{subject}' from {start_date} to {end_date}.")

    return "\n".join(lines)
