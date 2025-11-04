"""
Main meeting light control loop.

This module implements the core logic for monitoring calendar events
and controlling the Govee light based on meeting timing.
"""

import os
import time
import logging
from typing import Optional, Callable
from datetime import datetime, timezone
from dotenv import load_dotenv

# Import centralized configuration
from config import (
    APP_SUPPORT_PATH,
    ENV_FILE_PATH,
    LOG_FILE_PATH,
    LOG_FORMAT,
    LOG_LEVEL,
    LOOP_UPDATE_INTERVAL,
    HEALTH_CHECK_INTERVAL,
    MEETING_IDLE_THRESHOLD,
    MEETING_SOON_THRESHOLD,
    STATUS_IDLE,
    STATUS_SOON,
    STATUS_IMMINENT,
    STATUS_IN_MEETING,
    STATUS_NO_EVENTS,
    STATUS_CONNECTION_ISSUE,
    get_light_config_for_status
)

from govee import (
    set_light_off,
    set_light_color,
    set_light_brightness,
    set_color_temperature,
    check_connection_health,
    perform_health_check,
    reset_connection_health,
    reset_state
)

from gcal import get_upcoming_events, get_event_time_info

# Setup logging
os.makedirs(APP_SUPPORT_PATH, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=ENV_FILE_PATH)

# Health check tracking
last_health_check: Optional[float] = None


def set_light_for_status(status: str) -> bool:
    """
    Set the light to the appropriate color/brightness for a given meeting status.
    
    Args:
        status: Meeting status (from STATUS_* constants)
    
    Returns:
        True if all light commands succeeded, False otherwise
    """
    config = get_light_config_for_status(status)
    success = True
    
    if config['color'] is not None:
        # Set RGB color
        r, g, b = config['color']
        success = success and set_light_color(r, g, b)
    elif config['temperature'] is not None:
        # Set color temperature
        success = success and set_color_temperature(config['temperature'])
    
    # Set brightness
    success = success and set_light_brightness(config['brightness'])
    
    return success


def determine_meeting_status(now: datetime, start_time: datetime, end_time: datetime) -> str:
    """
    Determine the current meeting status based on timing.
    
    Args:
        now: Current time (UTC)
        start_time: Meeting start time (UTC)
        end_time: Meeting end time (UTC)
    
    Returns:
        Status string (one of STATUS_* constants)
    """
    seconds_until_start = (start_time - now).total_seconds()
    
    if start_time <= now <= end_time:
        return STATUS_IN_MEETING
    elif 0 < seconds_until_start <= MEETING_SOON_THRESHOLD:
        return STATUS_IMMINENT
    elif MEETING_SOON_THRESHOLD < seconds_until_start <= MEETING_IDLE_THRESHOLD:
        return STATUS_SOON
    else:
        return STATUS_IDLE


def run_meeting_loop(
    update_status: Optional[Callable[[str], None]] = None,
    update_next_meeting: Optional[Callable[[datetime], None]] = None
) -> None:
    """
    Main loop for monitoring calendar and controlling light.
    
    Args:
        update_status: Optional callback to update status in UI
        update_next_meeting: Optional callback to update next meeting time in UI
    """
    global last_health_check
    
    logger.info("Meeting Light loop started")
    logger.info(f"Configuration: Idle>{MEETING_IDLE_THRESHOLD}s, Soon<={MEETING_IDLE_THRESHOLD}s, Imminent<={MEETING_SOON_THRESHOLD}s")
    
    try:
        iteration = 0
        
        while True:
            iteration += 1
            now = datetime.now(timezone.utc)
            seconds_to_next_check = LOOP_UPDATE_INTERVAL - (now.second % LOOP_UPDATE_INTERVAL) - now.microsecond / 1_000_000
            
            # Periodic health check
            if last_health_check is None or (now.timestamp() - last_health_check) > HEALTH_CHECK_INTERVAL:
                logger.info("Performing periodic health check...")
                
                health_status, health_message = check_connection_health()
                logger.info(f"Connection health: {health_message}")
                
                if not health_status:
                    logger.warning("Connection appears unhealthy, attempting recovery...")
                    perform_health_check()
                    # Reset state tracking after recovery to force resync
                    reset_state()
                
                last_health_check = now.timestamp()
            
            # Fetch calendar events
            logger.debug(f"Fetching calendar events (iteration {iteration})")
            events = get_upcoming_events()

            if not events:
                logger.info("No upcoming events found.")
                status = STATUS_NO_EVENTS
                
                # Set light to idle state
                light_success = set_light_for_status(STATUS_IDLE)
                
                if not light_success:
                    status += STATUS_CONNECTION_ISSUE
                
                if update_status:
                    update_status(status)
                
                time.sleep(seconds_to_next_check)
                continue

            # Process the next event
            event = events[0]
            event_summary = event.get('summary', 'Untitled Event')
            
            # Get event times
            time_info = get_event_time_info(event)
            if time_info is None:
                logger.warning(f"Event '{event_summary}' missing valid time info, skipping")
                time.sleep(seconds_to_next_check)
                continue
            
            start_time, end_time = time_info
            
            # Convert to UTC for comparison
            start_time_utc = start_time.astimezone(timezone.utc)
            end_time_utc = end_time.astimezone(timezone.utc)
            
            seconds_until_start = (start_time_utc - now).total_seconds()

            # Update UI with next meeting time
            if update_next_meeting:
                update_next_meeting(start_time)

            # Determine meeting status
            status = determine_meeting_status(now, start_time_utc, end_time_utc)
            
            # Log the status with context
            if status == STATUS_IDLE:
                minutes_away = int(seconds_until_start / 60)
                logger.info(f"Meeting '{event_summary}' is {minutes_away} minutes away. Status: {status}")
            elif status == STATUS_SOON:
                minutes_away = int(seconds_until_start / 60)
                logger.info(f"Meeting '{event_summary}' in {minutes_away} minutes. Status: {status}")
            elif status == STATUS_IMMINENT:
                logger.info(f"Meeting '{event_summary}' starting in {int(seconds_until_start)} seconds! Status: {status}")
            elif status == STATUS_IN_MEETING:
                time_remaining = int((end_time_utc - now).total_seconds() / 60)
                logger.info(f"In meeting '{event_summary}' (ends in {time_remaining} min). Status: {status}")
            
            # Set light based on status
            light_success = set_light_for_status(status)
            
            # Check if light commands failed
            if not light_success:
                logger.warning("Light commands failed. Connection may be unstable.")
                status += STATUS_CONNECTION_ISSUE

            # Update UI status
            if update_status:
                update_status(status)

            logger.debug(f"Waiting {int(seconds_to_next_check)}s until next check...")
            time.sleep(seconds_to_next_check)

    except KeyboardInterrupt:
        logger.info("Meeting light loop stopped by user.")
        
    except Exception as e:
        logger.exception(f"Unexpected error in meeting loop: {e}")
        try:
            set_light_off()
            logger.info("Light turned off due to error.")
        except Exception as cleanup_error:
            logger.error(f"Failed to turn off light during error handling: {cleanup_error}")


if __name__ == "__main__":
    # Run the loop standalone (for testing)
    run_meeting_loop()