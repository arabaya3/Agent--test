import os
import requests
import json
import base64
from dotenv import load_dotenv
from shared.auth import get_access_token

load_dotenv()

def _graph_base():
    return "https://graph.microsoft.com/beta" if os.getenv("USE_GRAPH_BETA", "0") == "1" else "https://graph.microsoft.com/v1.0"

def _odata_quote(value: str) -> str:
    return value.replace("'", "''") if isinstance(value, str) else value

def _looks_like_conference_id(value: str) -> bool:
    return isinstance(value, str) and value.isdigit() and 6 <= len(value) <= 15

def resolve_online_meeting_id_from_conference_id(conference_id: str, headers, user_id: str, max_pages: int = 5):
    try:
        url = f"{_graph_base()}/users/{user_id}/onlineMeetings"
        params = {"$top": 50, "$select": "id,joinWebUrl,audioConferencing"}
        pages_checked = 0
        while url and pages_checked < max_pages:
            resp = requests.get(url, headers=headers, params=params if pages_checked == 0 else None)
            if resp.status_code == 403:
                print("Access denied while listing online meetings. Ensure OnlineMeetings.Read.All is granted and consented.")
                return None
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("value", []):
                ac = item.get("audioConferencing") or {}
                if ac.get("conferenceId") == conference_id:
                    return item.get("id")
            url = data.get("@odata.nextLink")
            pages_checked += 1
        print("No online meeting matched the provided conference ID.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error resolving meeting ID from conference ID: {e}")
        return None

def resolve_online_meeting_id_from_event_id(event_id: str, headers, user_id: str):
    try:
        url = f"{_graph_base()}/users/{user_id}/events/{event_id}"
        params = {"$select": "onlineMeeting,webLink"}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 403:
            print("Access denied reading event. Ensure Calendars.Read (Application) is granted and consented.")
            return None
        if resp.status_code == 404:
            print("Event not found for the provided ID.")
            return None
        resp.raise_for_status()
        evt = resp.json()
                                                                                                                           
        join_url = None
        om = evt.get("onlineMeeting") or {}
        join_url = om.get("joinUrl") or om.get("joinWebUrl")
        if not join_url:
            wl = evt.get("webLink")
            if isinstance(wl, str) and "teams.microsoft.com/l/meetup-join" in wl:
                join_url = wl
        if not join_url:
            print("Could not extract a Teams join URL from the event.")
            return None
        return resolve_online_meeting_id_from_join_url(join_url, headers, user_id)
    except requests.exceptions.RequestException as e:
        print(f"Error resolving meeting from event: {e}")
        return None

def resolve_online_meeting_id_from_join_url(join_url, headers, user_id):
    if not user_id:
        print("Error: A user_id (UPN/email) is required to resolve online meetings when using application permissions.")
        return None
    try:
        url = f"{_graph_base()}/users/{user_id}/onlineMeetings"
                                                      
        params = {"$filter": f"JoinWebUrl eq '{_odata_quote(join_url)}'"}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 403:
            print("Access denied while resolving online meeting by join URL. Ensure the app has OnlineMeetings.Read.All and admin consent.")
            return None
        resp.raise_for_status()
        value = resp.json().get("value", [])
        if not value:
            print("No online meeting found for the provided join URL.")
            return None
        meeting_id = value[0].get("id")
        if not meeting_id:
            print("Found meeting but no id field returned.")
            return None
        return meeting_id
    except requests.exceptions.RequestException as e:
        print(f"Error resolving meeting ID from join URL: {e}")
        return None

def get_transcript_by_meeting_id(meeting_id, headers, user_id=None):
                                                                                  
                                                                       
    if not user_id:
        user_id = os.getenv('DEFAULT_USER_ID')
    if not user_id:
        print("Error: user_id is required for transcript retrieval with application permissions. Set DEFAULT_USER_ID in .env or pass user_id.")
        return None

    if _looks_like_conference_id(meeting_id):
        print("Warning: The provided value looks like a dial-in conference ID, not an onlineMeeting ID. Provide the Teams join URL or the onlineMeeting id.")
    url = f"{_graph_base()}/users/{user_id}/onlineMeetings/{meeting_id}/transcripts"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            try:
                body = response.text[:500]
                print(f"Raw 403 body: {body}")
            except Exception:
                pass
            print(
                "Access denied: You do not have permission to access transcripts for this meeting.\n"
                "Please ensure your Azure admin has granted the required permissions and granted admin consent.\n"
                "Required (application) permission: OnlineMeetingTranscript.Read.All (and OnlineMeetings.Read.All to locate the meeting).\n"
                "Note: With app-only tokens, you must call /users/{USER_ID}/... (not /me) and the meetingId must be an onlineMeeting id."
            )
            return None
        if response.status_code == 404:
            print("Transcript not found for this meeting.")
            return None
        response.raise_for_status()
        data = response.json()
        transcripts = data.get("value", [])
        if not transcripts:
            print("No transcript available for this meeting.")
            return None
                                                     
        transcript_id = transcripts[0].get("id")
                                         
        transcript_url = f"{_graph_base()}/users/{user_id}/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content"
        content_headers = dict(headers)
        content_headers["Accept"] = "text/plain, text/vtt, application/json"
        transcript_resp = requests.get(transcript_url, headers=content_headers)
        transcript_resp.raise_for_status()
        return transcript_resp.text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving transcript: {e}")
        return None

def retrieve_transcript_by_meeting_id(meeting_id, user_id=None):
    print("============================================================")
    print("Meeting Transcript Retriever")
    print("============================================================")
    print(f"Input: {meeting_id}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

                                                                                                      
    try:
        parts = access_token.split(".")
        if len(parts) >= 2:
            padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
            has_roles = bool(payload.get("roles"))
            has_scp = bool(payload.get("scp"))
            if not has_roles and has_scp:
                print("Error: A delegated (user) token was detected. Transcript retrieval requires APPLICATION permissions (app-only token with app roles such as OnlineMeetingTranscript.Read.All).")
                return None
    except Exception:
                                                 
        pass

                                                      
    user_id = user_id or os.getenv('DEFAULT_USER_ID')
    if not user_id:
        print("Error: user_id is required. Set DEFAULT_USER_ID in .env or pass user_id explicitly.")
        return None

                                                                                            
    if isinstance(meeting_id, str) and (meeting_id.startswith("http://") or meeting_id.startswith("https://")):
        print("Detected join URL. Resolving online meeting ID...")
        resolved_id = resolve_online_meeting_id_from_join_url(meeting_id, headers, user_id)
        if not resolved_id:
            print("Could not resolve an online meeting from the join URL.")
            return None
        meeting_id = resolved_id
        print(f"Resolved onlineMeeting ID: {meeting_id}")
    elif _looks_like_conference_id(meeting_id):
        print("Detected dial-in conference ID. Attempting to resolve the onlineMeeting ID...")
        resolved_id = resolve_online_meeting_id_from_conference_id(meeting_id, headers, user_id)
        if not resolved_id:
            print("Could not resolve an online meeting from the conference ID.")
            return None
        meeting_id = resolved_id
        print(f"Resolved onlineMeeting ID: {meeting_id}")
    else:
                                                                             
        print("Input does not look like a join URL or conference ID. Attempting to resolve from event ID...")
        resolved_id = resolve_online_meeting_id_from_event_id(meeting_id, headers, user_id)
        if resolved_id:
            meeting_id = resolved_id
            print(f"Resolved onlineMeeting ID from event: {meeting_id}")

    print(f"Retrieving transcript for onlineMeeting ID: {meeting_id} as user: {user_id}")
    transcript = get_transcript_by_meeting_id(meeting_id, headers, user_id)
    if transcript:
        print("\nTranscript Content:\n")
        print(transcript)
    else:
        print("No transcript found or accessible for this meeting. Ensure transcription was enabled during the meeting and that the app has OnlineMeetingTranscript.Read.All.")
    return transcript

def main():
    print("============================================================")
    print("Meeting Transcript Retriever")
    print("============================================================")
    meeting_id = input("Enter meeting ID: ").strip()
    if not meeting_id:
        print("Error: Meeting ID is required")
        return
    retrieve_transcript_by_meeting_id(meeting_id)

if __name__ == "__main__":
    main()
