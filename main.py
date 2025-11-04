import os
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

from govee import (
    set_light_off, 
    set_light_color, 
    set_light_brightness, 
    set_color_temperature,
    check_connection_health,
    perform_health_check,
    reset_connection_health
)
from gcal import get_upcoming_events

# Setup logging
logger = logging.getLogger(__name__)

app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

# Health check configuration
HEALTH_CHECK_INTERVAL = 300  # 5 minutes
last_health_check = None

def run_meeting_loop(update_status=None, update_next_meeting=None):
    global last_health_check
    
    logger.info("Meeting Light loop started")
    
    try:
        iteration = 0
        
        while True:
            iteration += 1
            now = datetime.now(timezone.utc)
            seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000
            
            # Periodic health check (every 5 minutes)
            if last_health_check is None or (now.timestamp() - last_health_check) > HEALTH_CHECK_INTERVAL:
                logger.info("Performing periodic health check...")
                
                health_status, health_message = check_connection_health()
                logger.info(f"Connection health: {health_message}")
                
                if not health_status:
                    logger.warning("Connection appears unhealthy, attempting recovery...")
                    perform_health_check()
                
                last_health_check = now.timestamp()
            
            # Fetch calendar events
            logger.debug(f"Fetching calendar events (iteration {iteration})")
            events = get_upcoming_events()

            if not events:
                logger.info("No upcoming events found.")
                if update_status:
                    update_status("No upcoming events")
                time.sleep(seconds_to_next_minute)
                continue

            event = events[0]
            event_summary = event.get('summary', 'Untitled Event')
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            
            if not start_str or not end_str:
                logger.warning("Event missing start/end time, skipping")
                time.sleep(seconds_to_next_minute)
                continue
            
            start_time = datetime.fromisoformat(start_str).astimezone(timezone.utc)
            end_time = datetime.fromisoformat(end_str).astimezone(timezone.utc)
            seconds_until_start = (start_time - now).total_seconds()

            if update_next_meeting:
                update_next_meeting(start_time)

            logger.debug(f"Next meeting: '{event_summary}' in {int(seconds_until_start)}s")
            status = ""
            light_command_success = True

            # Determine light state based on meeting timing
            if seconds_until_start > 600:
                status = "Idle"
                logger.info(f"Meeting '{event_summary}' is more than 10 minutes away. Setting to normal.")
                light_command_success = set_color_temperature(2900) and set_light_brightness(10)
                
            elif 60 < seconds_until_start <= 600:
                status = "Meeting soon"
                minutes_away = int(seconds_until_start / 60)
                logger.info(f"Meeting '{event_summary}' in {minutes_away} minutes. Setting light to BLUE.")
                light_command_success = set_light_color(0, 0, 255) and set_light_brightness(50)
                
            elif 0 < seconds_until_start <= 60:
                status = "Meeting imminent"
                logger.info(f"Meeting '{event_summary}' starting in less than 1 minute! Setting light to RED.")
                light_command_success = set_light_color(255, 0, 0) and set_light_brightness(100)
                
            elif start_time <= now <= end_time:
                status = "In meeting"
                time_remaining = int((end_time - now).total_seconds() / 60)
                logger.info(f"In meeting '{event_summary}' (ends in {time_remaining} min). Setting light to WHITE.")
                light_command_success = set_light_color(255, 255, 255) and set_light_brightness(50)
                
            else:
                status = "Idle"
                logger.info(f"Meeting '{event_summary}' has ended. Setting to normal.")
                light_command_success = set_color_temperature(2900) and set_light_brightness(10)

            # Check if light commands failed
            if not light_command_success:
                logger.warning("Light commands failed. Connection may be unstable.")
                status += " (⚠️ Connection issue)"

            if update_status:
                update_status(status)

            logger.debug(f"Waiting {int(seconds_to_next_minute)}s until next check...")
            time.sleep(seconds_to_next_minute)

    except KeyboardInterrupt:
        logger.info("Meeting light loop stopped by user.")
        print("\nMeeting light loop stopped by user.")
        
    except Exception as e:
        logger.exception(f"Unexpected error in meeting loop: {e}")
        print(f"An error occurred: {e}")
        try:
            set_light_off()
            logger.info("Light turned off due to error.")
        except:
            logger.error("Failed to turn off light during error handling")