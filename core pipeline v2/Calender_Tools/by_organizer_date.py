def run_by_organizer_date() -> str:
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

    def search_meetings_by_organizer_date(organizer: str, date: str, headers: dict, user_id: str | None = None) -> list[dict]:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00Z")
            end_datetime = date_obj.strftime("%Y-%m-%dT23:59:59Z")
        except ValueError:
            lines.append("Error: Date must be in YYYY-MM-DD format")
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
                    meeting_organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "")
                    if organizer.lower() in meeting_organizer.lower():
                        filtered_meetings.append(meeting)

                all_meetings.extend(filtered_meetings)

                lines.append(
                    f"Retrieved {len(meetings)} meetings, filtered to {len(filtered_meetings)} by organizer... (Total filtered: {len(all_meetings)})"
                )

                url = data.get("@odata.nextLink")

                if len(all_meetings) >= 5000:
                    lines.append("Warning: Reached 5000 meetings limit.")
                    break

        except requests.exceptions.RequestException as e:
            lines.append(f"Error searching meetings: {e}")
            return []

        return all_meetings

    lines.append("============================================================")
    lines.append("Calendar Organizer Date Retriever")
    lines.append("============================================================")

    organizer = input("Enter organizer email address: ").strip()
    if not organizer:
        lines.append("Error: Organizer email is required")
        return "\n".join(lines)

    date = input("Enter date (YYYY-MM-DD): ").strip()
    if not date:
        lines.append("Error: Date is required")
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

    meetings = search_meetings_by_organizer_date(organizer, date, headers, user_id)

    lines.append("")
    lines.append("============================================================")
    lines.append("Retrieval Summary")
    lines.append("============================================================")
    lines.append(f"Total meetings found for organizer '{organizer}' on {date}: {len(meetings)}")

    if meetings:
        lines.append("")
        lines.append("Retrieved Meetings:")
        lines.append("============================================================")
        for i, meeting in enumerate(meetings, 1):
            start_time = meeting.get("start", {}).get("dateTime", "Unknown")
            end_time = meeting.get("end", {}).get("dateTime", "Unknown")
            subject = meeting.get("subject", "No Subject")
            organizer_email = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            attendees_count = len(meeting.get("attendees", []))

            lines.append(f"{i}. Subject: {subject}")
            lines.append(f"   ID: {meeting.get('id', 'Unknown')}")
            lines.append(f"   Organizer: {organizer_email}")
            lines.append(f"   Start: {start_time}")
            lines.append(f"   End: {end_time}")
            lines.append(f"   Attendees: {attendees_count}")
            lines.append(f"   Location: {meeting.get('location', {}).get('displayName', 'No location')}")
            lines.append("")
    else:
        lines.append(f"No meetings found for organizer '{organizer}' on {date}.")

    return "\n".join(lines)