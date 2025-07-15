import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_upcoming_events(max_results=5):
    now = datetime.utcnow().isoformat() + "Z"
    url = (
        f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
        f"?key={API_KEY}&timeMin={now}&maxResults={max_results}&singleEvents=true&orderBy=startTime"
    )

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to get calendar events: {response.status_code} - {response.text}")
        return []

    data = response.json()
    # print('data', data)
    return data.get("items", [])