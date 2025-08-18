import os
import requests
import json
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

def get_attendance_by_meeting_id(meeting_id, headers, user_id=None):
    if user_id:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/events/{meeting_id}/attendanceReports"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/events/{meeting_id}/attendanceReports"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print("Access denied: You do not have permission to access attendance for this meeting.")
            return None
        if response.status_code == 404:
            print("Attendance report not found for this meeting.")
            return None
        response.raise_for_status()
        data = response.json()
        reports = data.get("value", [])
        if not reports:
            print("No attendance report available for this meeting.")
            return None
                                                          
        return reports
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving attendance: {e}")
        return None

def retrieve_attendance_by_meeting_id(meeting_id, user_id=None):
    print("============================================================")
    print("Meeting Attendance Retriever")
    print("============================================================")
    print(f"Retrieving attendance for meeting ID: {meeting_id}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    reports = get_attendance_by_meeting_id(meeting_id, headers, user_id)
    if reports:
        for i, report in enumerate(reports, 1):
            print(f"Attendance Report {i}:")
            print(f"  Total Participants: {report.get('totalParticipantCount', 'N/A')}")
            print(f"  Meeting Start: {report.get('meetingStartDateTime', 'N/A')}")
            print(f"  Meeting End: {report.get('meetingEndDateTime', 'N/A')}")
            records = report.get('attendanceRecords', [])
            print(f"  Attendance Records ({len(records)}):")
            for rec in records:
                name = rec.get('identity', {}).get('displayName', 'Unknown')
                email = rec.get('emailAddress', 'Unknown')
                join_time = rec.get('joinDateTime', 'N/A')
                leave_time = rec.get('leaveDateTime', 'N/A')
                duration = rec.get('durationInSeconds', 'N/A')
                print(f"    - {name} <{email}> | Joined: {join_time} | Left: {leave_time} | Duration: {duration}s")
            print()
    else:
        print("No attendance report found or accessible for this meeting.")
    return reports

def main():
    print("============================================================")
    print("Meeting Attendance Retriever")
    print("============================================================")
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    retrieve_attendance_by_meeting_id(meeting_id)

if __name__ == "__main__":
    main()
