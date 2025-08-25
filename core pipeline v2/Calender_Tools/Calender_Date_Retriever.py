def retrieve_meetings_by_date(date: str, user_name: str | None = None) -> list[dict]:
    """
    Retrieve all meetings for a specific date from Microsoft Graph API
    
    Args:
        date (str): Date in YYYY-MM-DD format
        user_name (str, optional): User principal name (email/username).
                                   If None, searches for the current user
    
    Returns:
        list: List of meeting objects
    """

    # Local imports with safety net
    try:
        import os  # type: ignore
        import requests  # type: ignore
        from datetime import datetime  # type: ignore
        try:
            # Load .env if python-dotenv is available
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
        except Exception:
            pass
    except Exception:
        # If imports fail for any reason, return empty result gracefully
        print("Error: Required dependencies are not available.")
        return []

    # Credentials from environment (.env supported if dotenv is installed)
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")

    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        print("Error: Missing required environment variables: CLIENT_ID, CLIENT_SECRET, TENANT_ID")
        return []

    print("============================================================")
    print("Calendar Date Retriever")
    print("============================================================")
    print(f"Searching for meetings on: {date}")
    print("============================================================")

    # Get access token
    def get_access_token() -> str | None:
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_json = token_response.json()
            return token_json.get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None

    access_token = get_access_token()
    if not access_token:
        print("Error: Could not obtain access token")
        return []

    # Validate and format date
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return []

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Build URL using user_name (UPN) if provided
    if user_name:
        url = (
            f"https://graph.microsoft.com/v1.0/users/{user_name}/calendarView"
            f"?startDateTime={start_datetime}&endDateTime={end_datetime}"
            f"&$orderby=start/dateTime&$top=1000"
        )
    else:
        url = (
            f"https://graph.microsoft.com/v1.0/me/calendarView"
            f"?startDateTime={start_datetime}&endDateTime={end_datetime}"
            f"&$orderby=start/dateTime&$top=1000"
        )

    all_meetings: list[dict] = []

    # Paginate through all meetings
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            meetings = data.get("value", [])
            all_meetings.extend(meetings)

            print(f"Retrieved {len(meetings)} meetings... (Total: {len(all_meetings)})")
            url = data.get("@odata.nextLink")

            # Safety limit
            if len(all_meetings) >= 5000:
                print("Warning: Reached 5000 meetings limit.")
                break
    except requests.exceptions.RequestException as e:
        print(f"Error searching meetings: {e}")
        return []

    # Display results
    print("\n============================================================")
    print("Retrieval Summary")
    print("============================================================")
    print(f"Total meetings found: {len(all_meetings)}")

    if all_meetings:
        print("\nRetrieved Meetings:")
        print("============================================================")
        for i, meeting in enumerate(all_meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            print(f"{i}. Subject: {subject}")
            print(f"   Organizer: {organizer}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
            print(f"   Attendees: {attendees_count}")
            print(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            print()
    else:
        print("No meetings found for the specified date.")

    return all_meetings


# Example usage:
if __name__ == "__main__":
    date = "2025-08-21"  # Example date
    user_name = "Adan Al-Alawni"  # Example UPN (instead of user_id)
    meetings = retrieve_meetings_by_date(date, user_name)
