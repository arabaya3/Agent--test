import os
import sys
from email_by_id_retriever import retrieve_emails_by_ids, get_access_token
from email_by_sender_date_retriever import retrieve_emails_by_sender_date
from email_date_range_retriever import retrieve_emails_by_date_range
from email_subject_date_range_retriever import retrieve_emails_by_subject_date_range

def main():
    print("============================================================")
    print("Email Retriever Master Tool")
    print("============================================================")
    
    # Get authentication token once
    access_token = get_access_token()
    if not access_token:
        print("Authentication failed. Exiting...")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    while True:
        print("============================================================")
        print("Email Retriever Master Tool")
        print("============================================================")
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
            
            retrieve_emails_by_date_range(start_date, end_date, headers)
        
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
            
            retrieve_emails_by_subject_date_range(subject, start_date, end_date, headers)
        
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