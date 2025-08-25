def retrieve_meetings_by_date(date: str, user_name: str | None = None) -> str:
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
        # If imports fail for any reason, return message gracefully
        return "Error: Required dependencies are not available."

    # Credentials from environment (.env supported if dotenv is installed)
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")

    lines: list[str] = []

    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        return "Error: Missing required environment variables: CLIENT_ID, CLIENT_SECRET, TENANT_ID"

    lines.append("============================================================")
    lines.append("Calendar Date Retriever")
    lines.append("============================================================")
    lines.append(f"Searching for meetings on: {date}")
    lines.append("============================================================")

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
            lines.append(f"Error getting access token: {e}")
            return None

    access_token = get_access_token()
    if not access_token:
        lines.append("Error: Could not obtain access token")
        return "\n".join(lines)

    # Validate and format date
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
        end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        lines.append("Error: Date must be in YYYY-MM-DD format")
        return "\n".join(lines)

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Determine user principal name (UPN)
    if not user_name:
        # Prefer GRAPH_USERNAME, then fallback to DEFAULT_USER_ID
        user_name = os.getenv("GRAPH_USERNAME") or os.getenv("DEFAULT_USER_ID")

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

            lines.append(f"Retrieved {len(meetings)} meetings... (Total: {len(all_meetings)})")
            url = data.get("@odata.nextLink")

            # Safety limit
            if len(all_meetings) >= 5000:
                lines.append("Warning: Reached 5000 meetings limit.")
                break
    except requests.exceptions.RequestException as e:
        lines.append(f"Error searching meetings: {e}")
        return "\n".join(lines)

    # Display results
    lines.append("")
    lines.append("============================================================")
    lines.append("Retrieval Summary")
    lines.append("============================================================")
    lines.append(f"Total meetings found: {len(all_meetings)}")

    if all_meetings:
        lines.append("")
        lines.append("Retrieved Meetings:")
        lines.append("============================================================")
        for i, meeting in enumerate(all_meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            lines.append(f"{i}. Subject: {subject}")
            lines.append(f"   Organizer: {organizer}")
            lines.append(f"   Start: {start_time}")
            lines.append(f"   End: {end_time}")
            lines.append(f"   Attendees: {attendees_count}")
            lines.append(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            lines.append("")
    else:
        lines.append("No meetings found for the specified date.")

    return "\n".join(lines)


# Example usage:
if __name__ == "__main__":
    date = "2025-08-21"  # Example date
    user_name = "Adan Al-Alawni"  # Example UPN (instead of user_id)
    result = retrieve_meetings_by_date(date, user_name)
    print(result)
