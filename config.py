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