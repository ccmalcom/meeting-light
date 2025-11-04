import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException, Timeout

# Setup logging
logger = logging.getLogger(__name__)

app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# Configuration
REQUEST_TIMEOUT = 10  # seconds


def get_upcoming_events(max_results: int = 5) -> List[Dict]:
    """
    Fetch upcoming calendar events, filtering out all-day events, declined, and cancelled meetings.
    
    Args:
        max_results: Maximum number of events to return (default: 5)
    
    Returns:
        List of event dictionaries with dateTime fields (not all-day events)
        Returns empty list on error
    """
    now = datetime.utcnow().isoformat() + "Z"
    url = (
        f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
        f"?key={API_KEY}&timeMin={now}&maxResults={max_results * 2}&singleEvents=true&orderBy=startTime"
    )
    
    try:
        logger.debug("Fetching calendar events from Google Calendar API")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 401:
            logger.error("Google Calendar API authentication failed. Check your API key.")
            return []
        
        if response.status_code == 403:
            logger.error("Google Calendar API access forbidden. Check calendar ID and API permissions.")
            return []
        
        if response.status_code == 404:
            logger.error("Calendar not found. Check your GOOGLE_CALENDAR_ID setting.")
            return []
        
        if response.status_code != 200:
            logger.error(f"Failed to get calendar events: HTTP {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        all_events = data.get("items", [])
        
        # Filter events
        filtered_events = []
        for event in all_events:
            # Skip if we already have enough
            if len(filtered_events) >= max_results:
                break
            
            # Check if event is valid
            if not _is_valid_event(event):
                continue
            
            filtered_events.append(event)
        
        logger.info(f"Retrieved {len(filtered_events)} valid upcoming events")
        return filtered_events
    
    except Timeout:
        logger.error(f"Google Calendar API request timed out after {REQUEST_TIMEOUT}s")
        return []
    
    except RequestException as e:
        logger.error(f"Google Calendar API request failed: {str(e)}")
        return []
    
    except Exception as e:
        logger.exception(f"Unexpected error fetching calendar events: {e}")
        return []


def _is_valid_event(event: Dict) -> bool:
    """
    Check if an event should be included in the results.
    
    Filters out:
    - All-day events (no dateTime)
    - Declined meetings
    - Cancelled meetings
    
    Args:
        event: Event dictionary from Google Calendar API
    
    Returns:
        True if event is valid, False otherwise
    """
    # Check if event has dateTime (not all-day)
    start = event.get('start', {})
    if 'dateTime' not in start:
        logger.debug(f"Skipping all-day event: {event.get('summary', 'Untitled')}")
        return False
    
    # Check if event is cancelled
    if event.get('status') == 'cancelled':
        logger.debug(f"Skipping cancelled event: {event.get('summary', 'Untitled')}")
        return False
    
    # Check if user has declined the event
    # Look for the user's response status in attendees
    attendees = event.get('attendees', [])
    user_email = CALENDAR_ID  # Usually the calendar ID is the user's email
    
    for attendee in attendees:
        if attendee.get('email') == user_email:
            response_status = attendee.get('responseStatus')
            if response_status == 'declined':
                logger.debug(f"Skipping declined event: {event.get('summary', 'Untitled')}")
                return False
    
    # Check if event is marked as transparent (doesn't block calendar)
    if event.get('transparency') == 'transparent':
        logger.debug(f"Skipping transparent event: {event.get('summary', 'Untitled')}")
        return False
    
    return True


def get_event_time_info(event: Dict) -> Optional[tuple]:
    """
    Extract start and end times from an event.
    
    Args:
        event: Event dictionary from Google Calendar API
    
    Returns:
        Tuple of (start_datetime, end_datetime) or None if invalid
    """
    try:
        start_str = event['start'].get('dateTime')
        end_str = event['end'].get('dateTime')
        
        if not start_str or not end_str:
            return None
        
        start_time = datetime.fromisoformat(start_str)
        end_time = datetime.fromisoformat(end_str)
        
        return (start_time, end_time)
    
    except (KeyError, ValueError) as e:
        logger.warning(f"Failed to parse event times: {e}")
        return None