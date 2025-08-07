import os
import requests
import json
from dotenv import load_dotenv
import msal

load_dotenv()

def get_access_token():
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    
    if not client_id or not tenant_id:
        print("Error: CLIENT_ID and TENANT_ID must be set in .env file")
        return None
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.PublicClientApplication(client_id, authority=authority)
    
    scopes = [
        "https://graph.microsoft.com/Channel.ReadBasic.All",
        "https://graph.microsoft.com/Team.ReadBasic.All",
        "https://graph.microsoft.com/Calendars.Read"
    ]
    
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print("Error: Failed to create device flow")
        return None
    
    print("============================================================")
    print("Meeting Transcript Retriever - Authentication Required")
    print("============================================================")
    print(flow["message"])
    print("============================================================")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'Unknown error')}")
        return None

def get_transcript_by_meeting_id(meeting_id, headers):
    url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print("Access denied: You do not have permission to access transcripts for this meeting.\n" \
                  "Please ensure your Azure admin has granted the required permissions.\n" \
                  "Tried with: Channel.ReadBasic.All, Team.ReadBasic.All, Calendars.Read.\n" \
                  "You may need OnlineMeetings.Read.All or OnlineMeetings.ReadWrite.All.")
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
        # Get the first transcript (usually only one)
        transcript_id = transcripts[0].get("id")
        # Download the transcript content
        transcript_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content"
        transcript_resp = requests.get(transcript_url, headers=headers)
        transcript_resp.raise_for_status()
        return transcript_resp.text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving transcript: {e}")
        return None

def retrieve_transcript_by_meeting_id(meeting_id):
    print("============================================================")
    print("Meeting Transcript Retriever")
    print("============================================================")
    print(f"Retrieving transcript for meeting ID: {meeting_id}")
    print("============================================================")
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    transcript = get_transcript_by_meeting_id(meeting_id, headers)
    if transcript:
        print("\nTranscript Content:\n")
        print(transcript)
    else:
        print("No transcript found or accessible for this meeting.")
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
