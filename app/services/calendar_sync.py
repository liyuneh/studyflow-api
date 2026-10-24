from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN = Path("token.json")
CREDS = Path("credentials.json")


def _service():
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS), SCOPES)
            creds = flow.run_local_server(port=0)   # opens a browser once
        TOKEN.write_text(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def create_block_event(title, start, end, description="",
                       minutes_before=15, tz="Africa/Nairobi") -> str:
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": tz},
        "end": {"dateTime": end.isoformat(), "timeZone": tz},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": minutes_before},
                {"method": "email", "minutes": 60},
            ],
        },
    }
    created = _service().events().insert(calendarId="primary", body=event).execute()
    return created["id"]


def delete_event(event_id: str):
    _service().events().delete(calendarId="primary", eventId=event_id).execute()