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

def get_recent_meetings(headers, user_id=None, max_results=20):
    """Get recent meetings to choose from"""
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return []
    
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events?$top={max_results}&$orderby=start/dateTime desc"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("value", [])
        else:
            print(f"Error getting recent meetings: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving recent meetings: {e}")
        return []

def get_online_meeting_id_from_event(event_id, headers, user_id=None):
    """Get the online meeting ID from a calendar event"""
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return None
    
    # Try to get full event details including online meeting info
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/events/{event_id}?$select=id,subject,onlineMeeting,body,location"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            event_data = response.json()
            
            # Check for onlineMeeting object
            online_meeting = event_data.get('onlineMeeting')
            if online_meeting:
                print(f"Found online meeting data: {online_meeting}")
                # Try to get the online meeting ID from various sources
                join_url = online_meeting.get('joinUrl', '')
                if join_url:
                    print(f"Join URL found: {join_url}")
                    # Extract meeting ID from Teams URL
                    if 'meeting_' in join_url:
                        online_meeting_id = join_url.split('meeting_')[-1].split('/')[0]
                        print(f"Extracted meeting ID (encoded): {online_meeting_id}")
                        # URL decode the meeting ID
                        import urllib.parse
                        decoded_meeting_id = urllib.parse.unquote(online_meeting_id)
                        print(f"Extracted meeting ID (decoded): {decoded_meeting_id}")
                        return decoded_meeting_id
                    else:
                        # Try to get from the onlineMeeting object directly
                        online_meeting_id = online_meeting.get('id')
                        if online_meeting_id:
                            print(f"Direct meeting ID: {online_meeting_id}")
                            return online_meeting_id
                
                print("Found Teams meeting but couldn't extract meeting ID.")
                return None
            
            # Check if Teams meeting info is in the body or location
            body_content = event_data.get('body', {}).get('content', '')
            location_info = event_data.get('location', {}).get('displayName', '')
            
            # Look for Teams meeting URL in body or location
            teams_url = None
            if 'teams.microsoft.com' in body_content:
                # Extract Teams URL from body
                import re
                url_pattern = r'https://teams\.microsoft\.com/l/meetup-join/[^\s<>"\']*'
                matches = re.findall(url_pattern, body_content)
                if matches:
                    teams_url = matches[0]
            elif 'teams.microsoft.com' in location_info:
                teams_url = location_info
            
            if teams_url:
                print(f"Found Teams URL in content: {teams_url}")
                if 'meeting_' in teams_url:
                    online_meeting_id = teams_url.split('meeting_')[-1].split('/')[0]
                    print(f"Extracted meeting ID from content (encoded): {online_meeting_id}")
                    # URL decode the meeting ID
                    import urllib.parse
                    decoded_meeting_id = urllib.parse.unquote(online_meeting_id)
                    print(f"Extracted meeting ID from content (decoded): {decoded_meeting_id}")
                    return decoded_meeting_id
            
            print("This event does not have Teams meeting information.")
            return None
            
        elif response.status_code == 404:
            print("Event not found. The event ID might be invalid or the event has been deleted.")
            return None
        else:
            print(f"Error getting event details: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving event: {e}")
        return None

def get_attendance_by_meeting_id(meeting_id, headers, user_id=None):
    """Get attendance for a specific meeting ID"""
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return None
    
    print(f"Attempting to get attendance for meeting ID: {meeting_id}")
    
    # Method 1: Try using the meeting ID directly as an online meeting ID
    print("Method 1: Trying direct online meeting API...")
    online_meeting_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/onlineMeetings/{meeting_id}/attendanceReports"
    try:
        response = requests.get(online_meeting_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            reports = data.get("value", [])
            if reports:
                print("✅ Found attendance reports via direct online meeting API!")
                return reports
            else:
                print("No attendance reports found via direct API.")
        elif response.status_code == 404:
            print("404: Meeting not found in online meetings API.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Direct API error: {e}")
    
    # Method 2: Try to extract online meeting ID from calendar event
    print("Method 2: Trying to extract Teams meeting info from calendar event...")
    # Only try to extract from calendar event if the meeting_id looks like a calendar event ID
    if len(meeting_id) > 50 and 'AAMk' in meeting_id:  # Calendar event IDs are long and start with AAMk
        online_meeting_id = get_online_meeting_id_from_event(meeting_id, headers, user_id)
        if online_meeting_id and online_meeting_id != meeting_id:
            print(f"Found different online meeting ID: {online_meeting_id}")
            # Recursively call with the extracted meeting ID (but prevent infinite loop)
            return get_attendance_by_meeting_id(online_meeting_id, headers, user_id)
    else:
        print("Meeting ID appears to be an online meeting ID, skipping calendar event extraction.")
    
    # Method 3: Try different ID formats and endpoints
    print("Method 3: Trying different ID formats and endpoints...")
    
    # Try different variations of the meeting ID
    id_variations = [meeting_id]
    
    # If it's a Teams meeting ID, try different formats
    if '@' in meeting_id and 'thread.v2' in meeting_id:
        # Try without the @thread.v2 part
        base_id = meeting_id.split('@')[0]
        id_variations.append(base_id)
        # Try with just the meeting part
        if 'meeting_' in base_id:
            meeting_only = base_id.split('meeting_')[-1]
            id_variations.append(meeting_only)
    
    print(f"Trying ID variations: {id_variations}")
    
    for variation in id_variations:
        print(f"  Trying variation: {variation}")
        
        # Try with /users endpoint
        try:
            alt_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/onlineMeetings/{variation}/attendanceReports"
            response = requests.get(alt_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                reports = data.get("value", [])
                if reports:
                    print(f"✅ Found attendance reports with ID variation: {variation}")
                    return reports
                else:
                    print(f"  No reports found for variation: {variation}")
            elif response.status_code == 404:
                print(f"  404 for variation: {variation}")
            else:
                print(f"  Error {response.status_code} for variation: {variation}")
        except Exception as e:
            print(f"  Exception for variation {variation}: {e}")
    
    # Try /me endpoint (in case application permissions aren't properly set up)
    try:
        alt_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/attendanceReports"
        response = requests.get(alt_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            reports = data.get("value", [])
            if reports:
                print("✅ Found attendance reports via /me endpoint!")
                return reports
        elif response.status_code != 400:  # 400 is expected for application permissions
            print(f"Alternative endpoint status: {response.status_code}")
    except:
        pass
    
    print("❌ No attendance data could be retrieved using any method.")
    print("Possible reasons:")
    print("1. The meeting hasn't occurred yet or recently ended")
    print("2. Attendance tracking wasn't enabled for this meeting")
    print("3. This is a calendar event, not a Teams online meeting")
    print("4. Your app doesn't have the required permissions")
    print("5. The meeting has no participants recorded")
    
    return None

def display_attendance_report(reports):
    """Display attendance report in a nice format"""
    if not reports:
        print("No attendance data available.")
        return
    
    for i, report in enumerate(reports, 1):
        print(f"\n📊 ATTENDANCE REPORT #{i}")
        print("=" * 60)
        print(f"👥 Total Participants: {report.get('totalParticipantCount', 'N/A')}")
        print(f"🕐 Meeting Start: {report.get('meetingStartDateTime', 'N/A')}")
        print(f"🕐 Meeting End: {report.get('meetingEndDateTime', 'N/A')}")
        
        records = report.get('attendanceRecords', [])
        print(f"\n📋 Attendance Records ({len(records)}):")
        print("-" * 60)
        
        if records:
            for j, rec in enumerate(records, 1):
                name = rec.get('identity', {}).get('displayName', 'Unknown')
                email = rec.get('emailAddress', 'Unknown')
                join_time = rec.get('joinDateTime', 'N/A')
                leave_time = rec.get('leaveDateTime', 'N/A')
                duration = rec.get('durationInSeconds', 'N/A')
                
                print(f"{j:2d}. 👤 {name}")
                print(f"    📧 {email}")
                print(f"    ⏰ Joined: {join_time}")
                print(f"    ⏰ Left: {leave_time}")
                print(f"    ⏱️  Duration: {duration}s")
                print()
        else:
            print("No attendance records found.")
        
        print("=" * 60)

def main():
    print("============================================================")
    print("📊 MEETING ATTENDANCE RETRIEVER")
    print("============================================================")
    
    # Get user ID for application permissions
    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot fetch meeting attendance.")
        return
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Ask user how many meetings to retrieve
    while True:
        try:
            num_meetings = input("How many recent meetings do you want to retrieve? (1-50, default: 20): ").strip()
            if not num_meetings:
                num_meetings = 20
                break
            else:
                num_meetings = int(num_meetings)
                if 1 <= num_meetings <= 50:
                    break
                else:
                    print("Please enter a number between 1 and 50.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get recent meetings
    print(f"Fetching {num_meetings} recent meetings...")
    recent_meetings = get_recent_meetings(headers, target_user, num_meetings)
    
    if not recent_meetings:
        print("No recent meetings found.")
        return
    
    # Display meetings list
    print(f"\n📅 RECENT MEETINGS ({len(recent_meetings)} found):")
    print("=" * 80)
    
    for i, meeting in enumerate(recent_meetings, 1):
        subject = meeting.get('subject', 'No Subject')
        start_time = meeting.get('start', {}).get('dateTime', 'Unknown')
        meeting_id = meeting.get('id', 'Unknown')
        has_online_meeting = "✅" if meeting.get('onlineMeeting') else "❌"
        status = meeting.get('isCancelled', False)
        status_icon = "❌" if status else "✅"
        
        print(f"{i:2d}. {subject}")
        print(f"    🕐 Start: {start_time}")
        print(f"    🎯 Teams Meeting: {has_online_meeting}")
        print(f"    📊 Status: {status_icon} {'Cancelled' if status else 'Active'}")
        print(f"    🆔 ID: {meeting_id}")
        print("-" * 80)
    
    # Let user select a meeting
    while True:
        try:
            choice = input(f"\nSelect a meeting to get attendance (1-{len(recent_meetings)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Goodbye!")
                break
            
            meeting_index = int(choice) - 1
            if 0 <= meeting_index < len(recent_meetings):
                selected_meeting = recent_meetings[meeting_index]
                meeting_id = selected_meeting.get('id')
                subject = selected_meeting.get('subject', 'No Subject')
                
                print(f"\n🔍 Retrieving attendance for: {subject}")
                print("=" * 60)
                
                # Get attendance
                reports = get_attendance_by_meeting_id(meeting_id, headers, target_user)
                display_attendance_report(reports)
                
                # Ask if user wants to try another meeting
                another = input("\nTry another meeting? (y/n): ").strip().lower()
                if another != 'y':
                    print("Goodbye!")
                    break
            else:
                print(f"Please enter a number between 1 and {len(recent_meetings)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
