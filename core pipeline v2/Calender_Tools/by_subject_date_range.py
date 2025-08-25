def run_by_subject_date_range() -> str:
    lines: list[str] = []

    try:
        import os
        import requests
        import json  # noqa: F401 - kept for parity with original
        import sys
        from datetime import datetime
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
        except Exception:
            pass

        try:
            from shared.auth import get_access_token  # type: ignore
        except ModuleNotFoundError:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from shared.auth import get_access_token  # type: ignore
    except Exception as e:
        return f"Initialization error: {e}"

    def search_meetings_by_subject_date_range(subject: str, start_date: str, end_date: str, headers: dict, user_id: str | None = None) -> list[dict]:
        try:
            start_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_obj = datetime.strptime(end_date, "%Y-%m-%d")

            start_datetime = start_obj.strftime("%Y-%m-%dT00:00:00Z")
            end_datetime = end_obj.strftime("%Y-%m-%dT23:59:59Z")
        except ValueError:
            lines.append("Error: Dates must be in YYYY-MM-DD format")
            return []

        if user_id:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"
        else:
            url = f"https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&$orderby=start/dateTime&$top=1000"

        all_meetings: list[dict] = []

        try:
            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                meetings = data.get("value", [])

                filtered_meetings: list[dict] = []
                for meeting in meetings:
                    meeting_subject = meeting.get("subject", "")
                    if subject.lower() in meeting_subject.lower():
                        filtered_meetings.append(meeting)

                all_meetings.extend(filtered_meetings)

                lines.append(
                    f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by subject... (Total filtered: {len(all_meetings)})"
                )

                url = data.get("@odata.nextLink")

                if len(all_meetings) >= 5000:
                    lines.append("Warning: Reached 5000 meetings limit. Consider narrowing your search criteria.")
                    break

        except requests.exceptions.RequestException as e:
            lines.append(f"Error searching meetings: {e}")
            return []

        return all_meetings

    lines.append("============================================================")
    lines.append("Calendar Subject Date Range Retriever")
    lines.append("============================================================")

    subject = input("Enter subject keyword to search: ").strip()
    if not subject:
        lines.append("Error: Subject keyword is required")
        return "\n".join(lines)

    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if not start_date:
        lines.append("Error: Start date is required")
        return "\n".join(lines)

    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    if not end_date:
        lines.append("Error: End date is required")
        return "\n".join(lines)

    user_id = os.getenv("DEFAULT_USER_ID")
    if not user_id:
        lines.append("Error: DEFAULT_USER_ID not set in environment variables")
        return "\n".join(lines)

    access_token = get_access_token()
    if not access_token:
        lines.append("Error: Unable to obtain access token")
        return "\n".join(lines)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    meetings = search_meetings_by_subject_date_range(subject, start_date, end_date, headers, user_id)

    lines.append("")
    lines.append("============================================================")
    lines.append("Retrieval Summary")
    lines.append("============================================================")
    lines.append(f"Total meetings found with subject '{subject}' from {start_date} to {end_date}: {len(meetings)}")

    if meetings:
        lines.append("")
        lines.append("Retrieved Meetings:")
        lines.append("============================================================")
        for i, meeting in enumerate(meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            meeting_subject = meeting.get("subject", "No Subject")
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            lines.append(f"{i}. Subject: {meeting_subject}")
            lines.append(f"   ID: {meeting.get('id', 'Unknown')}")
            lines.append(f"   Organizer: {organizer}")
            lines.append(f"   Start: {start_time}")
            lines.append(f"   End: {end_time}")
            lines.append(f"   Attendees: {attendees_count}")
            lines.append(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            lines.append("")
    else:
        lines.append(f"No meetings found with subject '{subject}' in the specified date range.")

    return "\n".join(lines)