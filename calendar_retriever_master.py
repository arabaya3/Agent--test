import os
import sys
from calendar_by_date_retriever import retrieve_meetings_by_date
from calendar_by_organizer_date_retriever import retrieve_meetings_by_organizer_date
from calendar_date_range_retriever import retrieve_meetings_by_date_range
from calendar_subject_date_range_retriever import retrieve_meetings_by_subject_date_range

def main():
    while True:
        print("============================================================")
        print("Calendar Retriever Master Tool")
        print("============================================================")
        print("1. Get meetings by date")
        print("2. Retrieve meetings by organizer and date")
        print("3. Retrieve all meetings within date range")
        print("4. Retrieve meetings by subject and date range")
        print("5. Exit")
        print("============================================================")
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            print("\n" + "="*60)
            print("Get Meetings by Date")
            print("="*60)
            
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if not date:
                print("Error: Date is required")
                continue
            
            retrieve_meetings_by_date(date)
        
        elif choice == "2":
            print("\n" + "="*60)
            print("Retrieve Meetings by Organizer and Date")
            print("="*60)
            
            organizer = input("Enter organizer email address: ").strip()
            if not organizer:
                print("Error: Organizer email is required")
                continue
            
            date = input("Enter date (YYYY-MM-DD): ").strip()
            if not date:
                print("Error: Date is required")
                continue
            
            retrieve_meetings_by_organizer_date(organizer, date)
        
        elif choice == "3":
            print("\n" + "="*60)
            print("Retrieve All Meetings Within Date Range")
            print("="*60)
            
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            if not start_date:
                print("Error: Start date is required")
                continue
            
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if not end_date:
                print("Error: End date is required")
                continue
            
            retrieve_meetings_by_date_range(start_date, end_date)
        
        elif choice == "4":
            print("\n" + "="*60)
            print("Retrieve Meetings by Subject and Date Range")
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
            
            retrieve_meetings_by_subject_date_range(subject, start_date, end_date)
        
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