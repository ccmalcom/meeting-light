"""
Configuration constants for Meeting Light application.

This module centralizes all configuration values to make them easy to find and modify.
User customizations are loaded from user_config.json and override defaults.
"""

import os

# ============================================================================
# FILE PATHS
# ============================================================================

APP_SUPPORT_PATH = os.path.expanduser("~/Library/Application Support/MeetingLight")
ENV_FILE_PATH = os.path.join(APP_SUPPORT_PATH, ".env")
LOG_FILE_PATH = os.path.join(APP_SUPPORT_PATH, "meetinglight.log")

# ============================================================================
# TIMING CONFIGURATION (DEFAULTS)
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
# LIGHT COLORS AND BRIGHTNESS (DEFAULTS)
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
# STATUS MESSAGES
# ============================================================================

STATUS_IDLE = "Idle"
STATUS_SOON = "Meeting soon"
STATUS_IMMINENT = "Meeting imminent"
STATUS_IN_MEETING = "In meeting"
STATUS_NO_EVENTS = "No upcoming events"
STATUS_CONNECTION_ISSUE = " (⚠️ Connection issue)"

# ============================================================================
# USER CONFIG LOADING
# ============================================================================

def _load_user_config():
    """Load user configuration from JSON file if it exists."""
    import json
    user_config_path = os.path.join(APP_SUPPORT_PATH, "user_config.json")
    if os.path.exists(user_config_path):
        try:
            with open(user_config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# Load user config and override defaults
_user_config = _load_user_config()

# Override timing if user has customized
if 'meeting_idle_threshold' in _user_config:
    MEETING_IDLE_THRESHOLD = _user_config['meeting_idle_threshold']
if 'meeting_soon_threshold' in _user_config:
    MEETING_SOON_THRESHOLD = _user_config['meeting_soon_threshold']

# Override colors if user has customized
if 'color_soon' in _user_config:
    COLOR_SOON = tuple(_user_config['color_soon'])
if 'color_imminent' in _user_config:
    COLOR_IMMINENT = tuple(_user_config['color_imminent'])
if 'color_in_meeting' in _user_config:
    COLOR_IN_MEETING = tuple(_user_config['color_in_meeting'])
if 'color_idle_temp' in _user_config:
    TEMPERATURE_IDLE = _user_config['color_idle_temp']

# Override brightness if user has customized
if 'brightness_idle' in _user_config:
    BRIGHTNESS_IDLE = _user_config['brightness_idle']
if 'brightness_soon' in _user_config:
    BRIGHTNESS_SOON = _user_config['brightness_soon']
if 'brightness_imminent' in _user_config:
    BRIGHTNESS_IMMINENT = _user_config['brightness_imminent']
if 'brightness_in_meeting' in _user_config:
    BRIGHTNESS_IN_MEETING = _user_config['brightness_in_meeting']

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


def reload_config():
    """
    Reload configuration from user_config.json.
    
    This should be called after settings are updated to apply new values
    without restarting the app.
    """
    global MEETING_IDLE_THRESHOLD, MEETING_SOON_THRESHOLD
    global COLOR_SOON, COLOR_IMMINENT, COLOR_IN_MEETING, TEMPERATURE_IDLE
    global BRIGHTNESS_IDLE, BRIGHTNESS_SOON, BRIGHTNESS_IMMINENT, BRIGHTNESS_IN_MEETING
    
    # Reload user config
    user_config = _load_user_config()
    
    # Reset to defaults first
    MEETING_IDLE_THRESHOLD = 600
    MEETING_SOON_THRESHOLD = 60
    COLOR_SOON = (0, 0, 255)
    COLOR_IMMINENT = (255, 0, 0)
    COLOR_IN_MEETING = (255, 255, 255)
    TEMPERATURE_IDLE = 2900
    BRIGHTNESS_IDLE = 10
    BRIGHTNESS_SOON = 50
    BRIGHTNESS_IMMINENT = 100
    BRIGHTNESS_IN_MEETING = 50
    
    # Apply user overrides
    if 'meeting_idle_threshold' in user_config:
        MEETING_IDLE_THRESHOLD = user_config['meeting_idle_threshold']
    if 'meeting_soon_threshold' in user_config:
        MEETING_SOON_THRESHOLD = user_config['meeting_soon_threshold']
    if 'color_soon' in user_config:
        COLOR_SOON = tuple(user_config['color_soon'])
    if 'color_imminent' in user_config:
        COLOR_IMMINENT = tuple(user_config['color_imminent'])
    if 'color_in_meeting' in user_config:
        COLOR_IN_MEETING = tuple(user_config['color_in_meeting'])
    if 'color_idle_temp' in user_config:
        TEMPERATURE_IDLE = user_config['color_idle_temp']
    if 'brightness_idle' in user_config:
        BRIGHTNESS_IDLE = user_config['brightness_idle']
    if 'brightness_soon' in user_config:
        BRIGHTNESS_SOON = user_config['brightness_soon']
    if 'brightness_imminent' in user_config:
        BRIGHTNESS_IMMINENT = user_config['brightness_imminent']
    if 'brightness_in_meeting' in user_config:
        BRIGHTNESS_IN_MEETING = user_config['brightness_in_meeting']