import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import msal
from urllib.parse import quote
import time
from shared_email_ids import fetch_last_email_ids, get_cached_email_ids, get_access_token
from email_by_id_retriever import retrieve_emails_by_ids, get_access_token
from email_by_sender_date_retriever import retrieve_emails_by_sender_date
from email_date_range_retriever import retrieve_emails_by_date_range
from email_subject_date_range_retriever import retrieve_emails_by_subject_date_range

load_dotenv()

def search_emails(headers, email_ids):
    emails = []
    for eid in email_ids:
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
    print("Email Retriever Master")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        limit = int(input("How many recent emails do you want to fetch? (1-100, default 100): ").strip() or 100)
    except ValueError:
        limit = 100
    limit = min(max(1, limit), 100)
    fetch_last_email_ids(headers, limit=limit)
    email_ids = get_cached_email_ids(limit=limit)
    emails = search_emails(headers, email_ids)
    
    while True:
        print("============================================================")
        print("Email Retriever Master Tool")
        print("============================================================")
        print("EMAIL OPTIONS:")
        print("1. Retrieve emails by ID list")
        print("2. Retrieve emails by sender and date")
        print("3. Retrieve emails by date range")
        print("4. Retrieve emails by subject and date range")
        print("5. Exit")
        print("============================================================")
        
        choice = input("Select an option (1-5): ").strip()
        
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
                retrieve_emails_by_ids(email_ids, headers)
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
            
            retrieve_emails_by_sender_date(sender, date, headers)
        
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
            
            retrieve_emails_by_date_range(start_date, end_date, headers, email_ids)
        
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
            
            retrieve_emails_by_subject_date_range(subject, start_date, end_date, headers, email_ids)
        
        elif choice == "5":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")
        
        print("\n" + "="*60)
        input("Press Enter to continue...")
        print("\n" * 2)

if __name__ == "__main__":
    main() 