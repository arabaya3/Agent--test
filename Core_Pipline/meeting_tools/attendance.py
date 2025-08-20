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


def _odata_quote(value: str) -> str:
    return value.replace("'", "''") if isinstance(value, str) else value


def _is_url(value: str) -> bool:
    return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))


def resolve_online_meeting_id(input_value: str, headers: dict, user_id: str):
    """Resolve an input (join URL, event ID, or onlineMeeting ID) to an onlineMeeting ID."""
    # If URL → resolve by joinWebUrl
    if _is_url(input_value):
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings"
        params = {"$filter": f"JoinWebUrl eq '{_odata_quote(input_value)}'"}
        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                items = (resp.json() or {}).get("value", [])
                if items:
                    return items[0].get("id")
            else:
                print(f"Failed resolving meeting by join URL: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error resolving by join URL: {e}")
        return None

    # Try directly as onlineMeeting id
    try:
        test_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/{input_value}"
        resp = requests.get(test_url, headers=headers)
        if resp.status_code == 200:
            return (resp.json() or {}).get("id")
    except requests.exceptions.RequestException:
        pass

    # Treat as event id → read event, extract joinUrl, then resolve
    try:
        evt_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/events/{input_value}"
        params = {"$select": "id,subject,onlineMeeting,webLink,body,location"}
        evt_resp = requests.get(evt_url, headers=headers, params=params)
        if evt_resp.status_code == 200:
            evt = evt_resp.json() or {}
            subject = evt.get("subject", "Unknown")
            print(f"Found event: {subject}")
            
            # Check onlineMeeting object first
            om = evt.get("onlineMeeting") or {}
            if om:
                print(f"Online meeting data found: {om}")
                join_url = om.get("joinUrl") or om.get("joinWebUrl")
                if join_url:
                    print(f"Join URL from onlineMeeting: {join_url}")
                    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings"
                    params = {"$filter": f"JoinWebUrl eq '{_odata_quote(join_url)}'"}
                    resp = requests.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        items = (resp.json() or {}).get("value", [])
                        if items:
                            print(f"✅ Resolved to onlineMeeting ID: {items[0].get('id')}")
                            return items[0].get("id")
                        else:
                            print("No onlineMeeting found for this join URL")
                    else:
                        print(f"Error searching onlineMeetings: {resp.status_code}")
            
            # Check webLink
            web_link = evt.get("webLink")
            if web_link and "teams.microsoft.com" in web_link:
                print(f"Teams webLink found: {web_link}")
                url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings"
                params = {"$filter": f"JoinWebUrl eq '{_odata_quote(web_link)}'"}
                resp = requests.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    items = (resp.json() or {}).get("value", [])
                    if items:
                        print(f"✅ Resolved to onlineMeeting ID: {items[0].get('id')}")
                        return items[0].get("id")
            
            # Check body content for Teams URLs
            body_content = evt.get("body", {}).get("content", "")
            if "teams.microsoft.com" in body_content:
                import re
                url_pattern = r'https://teams\.microsoft\.com/l/meetup-join/[^\s<>"\']*'
                matches = re.findall(url_pattern, body_content)
                if matches:
                    teams_url = matches[0]
                    print(f"Teams URL found in body: {teams_url}")
                    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings"
                    params = {"$filter": f"JoinWebUrl eq '{_odata_quote(teams_url)}'"}
                    resp = requests.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        items = (resp.json() or {}).get("value", [])
                        if items:
                            print(f"✅ Resolved to onlineMeeting ID: {items[0].get('id')}")
                            return items[0].get("id")
            
            print("❌ No Teams meeting information found in this event")
            print("This event may not be a Teams meeting or attendance tracking may not be enabled")
            
        elif evt_resp.status_code == 404:
            print("❌ Event not found. Check if the event ID is correct.")
        else:
            print(f"❌ Error retrieving event: {evt_resp.status_code} {evt_resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error resolving from event: {e}")
    return None


def get_attendance_by_meeting_id(input_value, headers, user_id=None):
    """Get attendance for a meeting specified by onlineMeeting ID, join URL, or event ID."""
    target_user = user_id or os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: No user ID provided and DEFAULT_USER_ID not set")
        return None

    # Resolve to an onlineMeeting ID first
    online_meeting_id = resolve_online_meeting_id(input_value, headers, target_user)
    if not online_meeting_id:
        print("Could not resolve an onlineMeeting ID from the provided input.")
        return None

    reports_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/onlineMeetings/{online_meeting_id}/attendanceReports"
    try:
        response = requests.get(reports_url, headers=headers)
        if response.status_code != 200:
            print(f"Error retrieving attendance reports: {response.status_code} {response.text}")
            return None
        reports = (response.json() or {}).get("value", [])
        if not reports:
            print("No attendance reports available for this meeting.")
            return []

        # For each report, fetch its attendance records
        enriched = []
        for rep in reports:
            rep_id = rep.get("id")
            detail_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/onlineMeetings/{online_meeting_id}/attendanceReports/{rep_id}/attendanceRecords"
            rec_resp = requests.get(detail_url, headers=headers)
            if rec_resp.status_code == 200:
                records = (rec_resp.json() or {}).get("value", [])
            else:
                print(f"Warning: Failed to fetch attendance records for report {rep_id}: {rec_resp.status_code}")
                records = []
            rep_copy = dict(rep)
            rep_copy["attendanceRecords"] = records
            enriched.append(rep_copy)
        return enriched
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving attendance: {e}")
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
    print("📊 MEETING ATTENDANCE BY ID")
    print("============================================================")

    target_user = os.getenv("DEFAULT_USER_ID")
    if not target_user:
        print("Error: DEFAULT_USER_ID not set. Cannot fetch meeting attendance.")
        return

    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    meeting_input = input("Enter onlineMeeting ID, Teams join URL, or calendar event ID: ").strip()
    if not meeting_input:
        print("Error: Meeting identifier is required.")
        return

    reports = get_attendance_by_meeting_id(meeting_input, headers, target_user)
    if reports is None:
        print("\n💡 Tips for troubleshooting:")
        print("1. Make sure the meeting has already occurred")
        print("2. Ensure attendance tracking was enabled for the meeting")
        print("3. Try using a Teams join URL instead of event ID")
        print("4. Check if you have the required permissions (OnlineMeetings.Read.All)")
    else:
        display_attendance_report(reports)


if __name__ == "__main__":
    main()
