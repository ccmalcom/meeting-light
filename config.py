"""
Configuration constants for Meeting Light application.

This module centralizes all configuration values to make them easy to find and modify.
"""

# ============================================================================
# TIMING CONFIGURATION
# ============================================================================

# Meeting notification thresholds (in seconds)
MEETING_IDLE_THRESHOLD = 600  # 10 minutes - meeting is far away
MEETING_SOON_THRESHOLD = 60   # 1 minute - meeting is approaching
# If meeting is within MEETING_SOON_THRESHOLD, it's "imminent"
# If currently between start and end time, status is "in meeting"

# Loop and polling intervals (in seconds)
LOOP_UPDATE_INTERVAL = 60  # Check calendar every minute
HEALTH_CHECK_INTERVAL = 300  # Health check every 5 minutes (5 * 60)

# Working hours (24-hour format HH:MM)
# Light will only operate during these hours. Outside working hours, light turns off.
# These can be overridden via environment variables: WORKING_HOURS_START and WORKING_HOURS_END
DEFAULT_WORKING_HOURS_START = "08:00"  # 8 AM
DEFAULT_WORKING_HOURS_END = "20:00"    # 8 PM

# ============================================================================
# LIGHT COLORS AND BRIGHTNESS
# ============================================================================

# RGB color values (0-255)
COLOR_IDLE = None  # Use temperature instead
COLOR_SOON = (0, 0, 255)  # Blue
COLOR_IMMINENT = (255, 0, 0)  # Red
COLOR_IN_MEETING = (255, 255, 255)  # White

# Color temperature (Kelvin, 2000-9000)
TEMPERATURE_IDLE = 2900  # Warm white

# Brightness levels (0-100)
BRIGHTNESS_IDLE = 10
BRIGHTNESS_SOON = 50
BRIGHTNESS_IMMINENT = 100
BRIGHTNESS_IN_MEETING = 50

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Govee API settings
GOVEE_API_URL = "https://developer-api.govee.com/v1/devices/control"
GOVEE_API_TIMEOUT = 10  # seconds
GOVEE_MAX_RETRIES = 3
GOVEE_RETRY_DELAY = 2  # seconds (exponentially increased)
GOVEE_RATE_LIMIT_DELAY = 0.5  # seconds between API calls

# Google Calendar API settings
GCAL_API_TIMEOUT = 10  # seconds
GCAL_MAX_RESULTS = 5  # Number of events to fetch

# ============================================================================
# CONNECTION HEALTH
# ============================================================================

# Connection health monitoring
MAX_CONSECUTIVE_FAILURES = 5  # Alert threshold for consecutive failures
HEALTH_CHECK_TIMEOUT = 600  # 10 minutes - warn if no success in this time

# ============================================================================
# LOGGING
# ============================================================================

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# ============================================================================
# FILE PATHS
# ============================================================================

import os

APP_SUPPORT_PATH = os.path.expanduser("~/Library/Application Support/MeetingLight")
ENV_FILE_PATH = os.path.join(APP_SUPPORT_PATH, ".env")
LOG_FILE_PATH = os.path.join(APP_SUPPORT_PATH, "meetinglight.log")

# ============================================================================
# STATUS MESSAGES
# ============================================================================

STATUS_IDLE = "Idle"
STATUS_SOON = "Meeting soon"
STATUS_IMMINENT = "Meeting imminent"
STATUS_IN_MEETING = "In meeting"
STATUS_NO_EVENTS = "No upcoming events"
STATUS_CONNECTION_ISSUE = " (⚠️ Connection issue)"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_light_config_for_status(status: str) -> dict:
    """
    Get the light configuration (color/temperature and brightness) for a given status.

    Args:
        status: One of STATUS_IDLE, STATUS_SOON, STATUS_IMMINENT, STATUS_IN_MEETING

    Returns:
        Dictionary with 'color', 'temperature', and 'brightness' keys
    """
    configs = {
        STATUS_IDLE: {
            'color': COLOR_IDLE,
            'temperature': TEMPERATURE_IDLE,
            'brightness': BRIGHTNESS_IDLE
        },
        STATUS_SOON: {
            'color': COLOR_SOON,
            'temperature': None,
            'brightness': BRIGHTNESS_SOON
        },
        STATUS_IMMINENT: {
            'color': COLOR_IMMINENT,
            'temperature': None,
            'brightness': BRIGHTNESS_IMMINENT
        },
        STATUS_IN_MEETING: {
            'color': COLOR_IN_MEETING,
            'temperature': None,
            'brightness': BRIGHTNESS_IN_MEETING
        }
    }

    return configs.get(status, configs[STATUS_IDLE])


def is_within_working_hours(current_time, start_time: str, end_time: str) -> bool:
    """
    Check if the current time falls within working hours.

    Args:
        current_time: datetime object representing the current time
        start_time: Working hours start in 24-hour format (HH:MM)
        end_time: Working hours end in 24-hour format (HH:MM)

    Returns:
        True if current time is within working hours, False otherwise
    """
    from datetime import time as dt_time

    try:
        # Parse the working hours
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))

        start = dt_time(start_hour, start_min)
        end = dt_time(end_hour, end_min)

        # Get current time of day
        current = current_time.time()

        # Handle cases where end time is before start time (e.g., night shift)
        if end < start:
            # Working hours span midnight (e.g., 20:00 to 08:00)
            return current >= start or current < end
        else:
            # Normal case (e.g., 08:00 to 20:00)
            return start <= current < end

    except (ValueError, AttributeError) as e:
        # If parsing fails, default to always within working hours
        import logging
        logging.getLogger(__name__).warning(f"Failed to parse working hours: {e}. Defaulting to always on.")
        return True