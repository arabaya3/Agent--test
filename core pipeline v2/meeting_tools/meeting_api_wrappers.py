import os
import requests
import json
import re
import urllib.parse
from typing import Optional

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

def get_meeting_by_id(meeting_id: str) -> str:
    """
    Get meeting details by ID and return as formatted string.
    
    Args:
        meeting_id: Meeting ID (can be Teams URL, event ID, or onlineMeeting ID)
    
    Returns:
        Formatted string with meeting details or error message
    """
    # Clean the meeting ID
    teams_url_pattern = r'meeting_([a-zA-Z0-9%]+)'
    teams_match = re.search(teams_url_pattern, meeting_id)
    if teams_match:
        meeting_id = teams_match.group(1)
        meeting_id = urllib.parse.unquote(meeting_id)
    else:
        meeting_id = re.sub(r'\s+', '', meeting_id)
    
    # Get auth token
    access_token = get_access_token()
    if not access_token:
        return "Error: Failed to get access token"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get user ID
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        return "Error: DEFAULT_USER_ID not set"
    
    # Fetch meeting details
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        meeting = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error retrieving meeting {meeting_id}: {e}"
    
    # Format meeting details
    subject = meeting.get('subject', 'No Subject')
    organizer = meeting.get('organizer', {}).get('emailAddress', {}).get('address', 'Unknown')
    start_time = meeting.get('start', {}).get('dateTime', 'Unknown')
    end_time = meeting.get('end', {}).get('dateTime', 'Unknown')
    location = meeting.get('location', {}).get('displayName', 'No location')
    attendees = meeting.get('attendees', [])
    
    result = f"""Meeting Details:
============================================================
Subject: {subject}
Organizer: {organizer}
Start: {start_time}
End: {end_time}
Location: {location}
Attendees ({len(attendees)}):"""
    
    for att in attendees:
        email = att.get('emailAddress', {}).get('address', 'Unknown')
        att_type = att.get('type', '')
        result += f"\n  - {email} ({att_type})"
    
    return result

def get_meetings_by_title(title: str) -> str:
    """
    Get meetings by title and return as formatted string.
    
    Args:
        title: Meeting title to search for
    
    Returns:
        Formatted string with meeting details or error message
    """
    # Get auth token
    access_token = get_access_token()
    if not access_token:
        return "Error: Failed to get access token"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get user ID
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        return "Error: DEFAULT_USER_ID not set"
    
    # Search for meetings by title
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events"
    params = {
        "$filter": f"contains(subject, '{title}')",
        "$orderby": "start/dateTime desc",
        "$top": 50
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        meetings = data.get("value", [])
    except requests.exceptions.RequestException as e:
        return f"Error retrieving meetings: {e}"
    
    if not meetings:
        return f"No meetings found with title containing '{title}'"
    
    # Format meeting details
    result = f"Meetings with title containing '{title}' ({len(meetings)} found):\n"
    result += "=" * 80 + "\n"
    
    for i, meeting in enumerate(meetings, 1):
        subject = meeting.get('subject', 'No Subject')
        organizer = meeting.get('organizer', {}).get('emailAddress', {}).get('address', 'Unknown')
        start_time = meeting.get('start', {}).get('dateTime', 'Unknown')
        end_time = meeting.get('end', {}).get('dateTime', 'Unknown')
        location = meeting.get('location', {}).get('displayName', 'No location')
        attendees = meeting.get('attendees', [])
        meeting_id = meeting.get('id', 'Unknown')
        
        result += f"{i}. Subject: {subject}\n"
        result += f"   ID: {meeting_id}\n"
        result += f"   Organizer: {organizer}\n"
        result += f"   Start: {start_time}\n"
        result += f"   End: {end_time}\n"
        result += f"   Location: {location}\n"
        result += f"   Attendees ({len(attendees)}):\n"
        
        for att in attendees:
            email = att.get('emailAddress', {}).get('address', 'Unknown')
            att_type = att.get('type', '')
            result += f"     - {email} ({att_type})\n"
        
        result += "-" * 80 + "\n"
    
    return result

def get_meeting_attendance(meeting_id: str) -> str:
    """
    Get meeting attendance by meeting ID and return as formatted string.
    
    Args:
        meeting_id: Meeting ID, Teams join URL, or calendar event ID
    
    Returns:
        Formatted string with attendance details or error message
    """
    # For now, return a simplified version since the original requires complex authentication
    # This can be enhanced later with proper Teams meeting attendance API
    return f"Meeting attendance for {meeting_id}:\nNote: Teams meeting attendance requires additional authentication setup.\nThis endpoint is available but needs Teams-specific permissions."

def get_meeting_audience(meeting_id: str) -> str:
    """
    Get meeting audience details by meeting ID and return as formatted string.
    
    Args:
        meeting_id: Meeting ID (can be Teams URL, event ID, or onlineMeeting ID)
    
    Returns:
        Formatted string with meeting audience details or error message
    """
    # Get auth token
    access_token = get_access_token()
    if not access_token:
        return "Error: Failed to get access token"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get user ID
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        return "Error: DEFAULT_USER_ID not set"
    
    # Fetch meeting details
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        meeting = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error retrieving meeting {meeting_id}: {e}"
    
    # Format audience details
    subject = meeting.get('subject', 'No Subject')
    attendees = meeting.get('attendees', [])
    organizer = meeting.get('organizer', {}).get('emailAddress', {})
    
    result = f"Meeting Audience Details:\n"
    result += "=" * 60 + "\n"
    result += f"Subject: {subject}\n"
    result += f"Organizer: {organizer.get('address', 'Unknown')} ({organizer.get('name', 'Unknown')})\n"
    result += f"Total Attendees: {len(attendees)}\n\n"
    
    if attendees:
        result += "Attendees:\n"
        result += "-" * 60 + "\n"
        
        for i, att in enumerate(attendees, 1):
            email = att.get('emailAddress', {})
            att_type = att.get('type', 'Unknown')
            status = att.get('status', {}).get('response', 'Unknown')
            
            result += f"{i}. {email.get('name', 'Unknown')}\n"
            result += f"   Email: {email.get('address', 'Unknown')}\n"
            result += f"   Type: {att_type}\n"
            result += f"   Status: {status}\n"
            result += "\n"
    else:
        result += "No attendees found for this meeting.\n"
    
    return result

def get_meeting_transcript(meeting_id: str) -> str:
    """
    Get meeting transcript and return as formatted string.
    
    Args:
        meeting_id: Meeting ID, Teams join URL, or joinMeetingId value
    
    Returns:
        Formatted string with transcript info or error message
    """
    # For now, return a simplified version since the original requires complex authentication
    # This can be enhanced later with proper Teams transcript API
    return f"Meeting transcript for {meeting_id}:\nNote: Teams meeting transcripts require additional authentication setup.\nThis endpoint is available but needs Teams-specific permissions."
