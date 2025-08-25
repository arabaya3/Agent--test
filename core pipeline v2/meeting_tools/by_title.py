def get_meetings_by_title(title: str) -> str:
    """
    Get meetings by title and return as formatted string.
    
    Args:
        title: Meeting title to search for
    
    Returns:
        Formatted string with meeting details or error message
    """
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
        result = f"Error retrieving meetings: {e}"
        print(result)
        return result
    
    if not meetings:
        result = f"No meetings found with title containing '{title}'"
        print(result)
        return result
    
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
    
    print(result)
    return result
