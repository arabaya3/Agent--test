import os
from dotenv import load_dotenv

load_dotenv()


def clear_screen() -> None:
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass


def pause() -> None:
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        pass


def menu_email() -> None:
    while True:
        clear_screen()
        print("================ Email Tools ================")
        print("1) Email by IDs (with conversation)")
        print("2) Emails by sender within date range")
        print("3) Emails by date range")
        print("4) Emails by subject within date range")
        print("5) Get attachments by email ID (conversation)")
        print("B) Back")
        choice = input("Select: ").strip().lower()
        if choice == '1':
            try:
                from email_tools import by_id as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '2':
            try:
                from email_tools import by_sender_date as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '3':
            try:
                from email_tools import by_date_range as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '4':
            try:
                from email_tools import by_subject_date_range as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '5':
            try:
                from email_tools import shared_files_simple as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == 'b':
            return


def menu_calendar() -> None:
    while True:
        clear_screen()
        print("=============== Calendar Tools ===============")
        print("1) Meetings by date")
        print("2) Meetings by organizer and date")
        print("3) Meetings by date range")
        print("4) Meetings by subject within date range")
        print("B) Back")
        choice = input("Select: ").strip().lower()
        try:
            if choice == '1':
                from calendar_tools import by_date as mod
                mod.main()
                pause()
            elif choice == '2':
                from calendar_tools import by_organizer_date as mod
                mod.main()
                pause()
            elif choice == '3':
                from calendar_tools import by_date_range as mod
                mod.main()
                pause()
            elif choice == '4':
                from calendar_tools import by_subject_date_range as mod
                mod.main()
                pause()
            elif choice == 'b':
                return
        except Exception as e:
            print(f"Error: {e}")
            pause()


def menu_meetings() -> None:
    while True:
        clear_screen()
        print("================ Meeting Tools ===============")
        print("1) Meeting by ID")
        print("2) Meetings by title")
        print("3) Meeting transcript by meeting ID")
        print("4) Meeting audience by meeting ID")
        print("5) Meeting attendance by meeting ID")
        print("B) Back")
        choice = input("Select: ").strip().lower()
        try:
            if choice == '1':
                from meeting_tools import by_id as mod
                mod.main()
                pause()
            elif choice == '2':
                from meeting_tools import by_title as mod
                mod.main()
                pause()
            elif choice == '3':
                from meeting_tools import transcript as mod
                mod.main()
                pause()
            elif choice == '4':
                from meeting_tools import audience as mod
                mod.main()
                pause()
            elif choice == '5':
                from meeting_tools import attendance as mod
                mod.main()
                pause()
            elif choice == 'b':
                return
        except Exception as e:
            print(f"Error: {e}")
            pause()


def menu_onedrive() -> None:
    while True:
        clear_screen()
        print("================ OneDrive Tools ===============")
        print("1) List files")
        print("2) Download file")
        print("3) Upload file")
        print("4) View shared items")
        print("B) Back")
        choice = input("Select: ").strip().lower()
        if choice == '1':
            try:
                from onedrive_tools import list_files as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '2':
            try:
                from onedrive_tools import retrieve_files as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '3':
            try:
                from onedrive_tools import upload_files as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == '4':
            try:
                from onedrive_tools import shared_with_me as mod
                mod.main()
            except Exception as e:
                print(f"Error: {e}")
            pause()
        elif choice == 'b':
            return


def main() -> None:
    while True:
        clear_screen()
        print("================ Core Pipeline Tools ================")
        print("1) Email tools")
        print("2) Calendar tools")
        print("3) Meeting tools")
        print("4) OneDrive tools")
        print("Q) Quit")
        choice = input("Select: ").strip().lower()
        if choice == '1':
            menu_email()
        elif choice == '2':
            menu_calendar()
        elif choice == '3':
            menu_meetings()
        elif choice == '4':
            menu_onedrive()
        elif choice == 'q':
            break


if __name__ == "__main__":
    main()
