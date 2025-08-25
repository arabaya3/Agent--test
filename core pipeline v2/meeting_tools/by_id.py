def get_meeting_by_id(meeting_id: str) -> str:
    """
    Get meeting details by ID and return as formatted string.
    
    Args:
        meeting_id: Meeting ID (can be Teams URL, event ID, or onlineMeeting ID)
    
    Returns:
        Formatted string with meeting details or error message
    """
    import os
    import requests
    import json
    import re
    import urllib.parse
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
        result = "Error: Failed to get access token"
        print(result)
        return result
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get user ID
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        result = "Error: DEFAULT_USER_ID not set"
        print(result)
        return result
    
    # Fetch meeting details
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{meeting_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        meeting = response.json()
    except requests.exceptions.RequestException as e:
        result = f"Error retrieving meeting {meeting_id}: {e}"
        print(result)
        return result
    
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
    
    print(result)
    return result
