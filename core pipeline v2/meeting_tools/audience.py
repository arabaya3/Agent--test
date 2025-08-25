def get_meeting_audience(meeting_id: str) -> str:
    """
    Get meeting audience details by meeting ID and return as formatted string.
    
    Args:
        meeting_id: Meeting ID (can be Teams URL, event ID, or onlineMeeting ID)
    
    Returns:
        Formatted string with meeting audience details or error message
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
    
    print(result)
    return result
