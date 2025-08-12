import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import msal
from urllib.parse import quote
import time
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from shared.auth import get_access_token
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from calendar_tools.by_date import retrieve_meetings_by_date
from calendar_tools.by_organizer_date import retrieve_meetings_by_organizer_date
from calendar_tools.by_date_range import retrieve_meetings_by_date_range
from calendar_tools.by_subject_date_range import retrieve_meetings_by_subject_date_range
from meeting_tools.by_id import retrieve_meeting_by_id
from meeting_tools.by_title import retrieve_meetings_by_title
from meeting_tools.transcript import retrieve_transcript_by_meeting_id
from meeting_tools.audience import retrieve_meeting_audience
from meeting_tools.attendance import retrieve_attendance_by_meeting_id

load_dotenv()

def search_emails(headers, email_ids, user_id=None):
    emails = []
    for eid in email_ids:
        if user_id:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{eid}"
        else:
            url = f"https://graph.microsoft.com/v1.0/me/messages/{eid}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                emails.append(response.json())
        except Exception:
            continue
    print(f"[DEBUG] Found {len(emails)} emails from {len(email_ids)} recent emails.")
    return emails

def main():
    print("============================================================")
    print("Assistant Retriever Master")
    print("============================================================")
    while True:
        print("============================================================")
        print("EMAIL OPTIONS:")
        print("1. Retrieve emails by ID list")
        print("2. Retrieve emails by sender and date")
        print("3. Retrieve emails by date range")
        print("4. Retrieve emails by subject and date range")
        print("CALENDAR OPTIONS:")
        print("5. Get meetings by date")
        print("6. Retrieve meetings by organizer and date")
        print("7. Retrieve all meetings within date range")
        print("8. Retrieve meetings by subject and date range")
        print("MEETING OPTIONS:")
        print("9. Get meeting by ID")
        print("10. Get meeting by title")
        print("11. Get transcript from meeting ID")
        print("12. Get audience (attendees) from meeting ID")
        print("13. Get attendance from meeting ID")
        print("14. Exit")
        print("============================================================")
        choice = input("Select an option (1-14): ").strip()
        if choice in {"1", "2", "3", "4"}:
            access_token = get_access_token()
            if not access_token:
                continue
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
                
            try:
                limit = int(input("How many recent emails do you want to fetch? (1-100, default 100): ").strip() or 100)
            except ValueError:
                limit = 100
            limit = min(max(1, limit), 100)
            fetch_last_email_ids(headers, limit=limit, user_id=user_id)
            email_ids = get_cached_email_ids(limit=limit)
            emails = search_emails(headers, email_ids, user_id)
        if choice == "1":
            print("\n" + "="*60)
            print("Retrieve Emails by ID List")
            print("="*60)
            print("Enter email IDs (one per line, press Enter twice when done):")
            email_ids = []
            while True:
                email_id = input().strip()
                if not email_id:
                    break
                email_ids.append(email_id)
            if email_ids:
                retrieve_emails_by_ids(email_ids, headers, user_id)
            else:
                print("No email IDs provided.")
        elif choice == "2":
            print("\n" + "="*60)
            print("Retrieve Emails by Sender and Date")
            print("="*60)
            sender = input("Enter sender email address: ").strip()
            if not sender:
                print("Error: Sender email is required")
                continue
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if not date:
                print("Error: Date is required")
                continue
            retrieve_emails_by_sender_date(sender, date, headers, user_id)
        elif choice == "3":
            print("\n" + "="*60)
            print("Retrieve Emails by Date Range")
            print("="*60)
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            if not start_date:
                print("Error: Start date is required")
                continue
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if not end_date:
                print("Error: End date is required")
                continue
            retrieve_emails_by_date_range(start_date, end_date, headers, email_ids, user_id)
        elif choice == "4":
            print("\n" + "="*60)
            print("Retrieve Emails by Subject and Date Range")
            print("="*60)
            subject = input("Enter subject keyword to search: ").strip()
            if not subject:
                print("Error: Subject keyword is required")
                continue
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            if not start_date:
                print("Error: Start date is required")
                continue
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if not end_date:
                print("Error: End date is required")
                continue
            retrieve_emails_by_subject_date_range(subject, start_date, end_date, headers, email_ids, user_id)
        elif choice == "5":
            print("\n" + "="*60)
            print("Get Meetings by Date")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if not date:
                print("Error: Date is required")
                continue
            retrieve_meetings_by_date(date, user_id)
        elif choice == "6":
            print("\n" + "="*60)
            print("Retrieve Meetings by Organizer and Date")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            organizer = input("Enter organizer email address: ").strip()
            if not organizer:
                print("Error: Organizer email is required")
                continue
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if not date:
                print("Error: Date is required")
                continue
            retrieve_meetings_by_organizer_date(organizer, date, user_id)
        elif choice == "7":
            print("\n" + "="*60)
            print("Retrieve All Meetings Within Date Range")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            if not start_date:
                print("Error: Start date is required")
                continue
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if not end_date:
                print("Error: End date is required")
                continue
            retrieve_meetings_by_date_range(start_date, end_date, user_id)
        elif choice == "8":
            print("\n" + "="*60)
            print("Retrieve Meetings by Subject and Date Range")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            subject = input("Enter subject keyword to search: ").strip()
            if not subject:
                print("Error: Subject keyword is required")
                continue
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            if not start_date:
                print("Error: Start date is required")
                continue
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if not end_date:
                print("Error: End date is required")
                continue
            retrieve_meetings_by_subject_date_range(subject, start_date, end_date, user_id)
        elif choice == "9":
            print("\n" + "="*60)
            print("Get Meeting by ID")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            meeting_id = input("Enter meeting ID: ").strip()
            if not meeting_id:
                print("Error: Meeting ID is required")
                continue
            retrieve_meeting_by_id(meeting_id, user_id)
        elif choice == "10":
            print("\n" + "="*60)
            print("Get Meeting by Title")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            title = input("Enter meeting title or keyword: ").strip()
            if not title:
                print("Error: Meeting title is required")
                continue
            retrieve_meetings_by_title(title, user_id)
        elif choice == "11":
            print("\n" + "="*60)
            print("Get Transcript from Meeting ID")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            meeting_id = input("Enter meeting ID: ").strip()
            if not meeting_id:
                print("Error: Meeting ID is required")
                continue
            retrieve_transcript_by_meeting_id(meeting_id, user_id)
        elif choice == "12":
            print("\n" + "="*60)
            print("Get Audience (Attendees) from Meeting ID")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            meeting_id = input("Enter meeting ID: ").strip()
            if not meeting_id:
                print("Error: Meeting ID is required")
                continue
            retrieve_meeting_audience(meeting_id, user_id)
        elif choice == "13":
            print("\n" + "="*60)
            print("Get Attendance from Meeting ID")
            print("="*60)
            # For application permissions, we need a user ID
            user_id = input("Enter user ID or email address (for application permissions): ").strip()
            if not user_id:
                print("Error: User ID is required for application permissions")
                continue
            meeting_id = input("Enter meeting ID: ").strip()
            if not meeting_id:
                print("Error: Meeting ID is required")
                continue
            retrieve_attendance_by_meeting_id(meeting_id, user_id)
        elif choice == "14":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1-14.")
        print("\n" + "="*60)
        input("Press Enter to continue...")
        print("\n" * 2)

if __name__ == "__main__":
    main() 