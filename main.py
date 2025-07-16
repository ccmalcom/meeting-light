import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

from govee import set_light_off, set_light_color, set_light_brightness, set_color_temperature, set_light_brightness
from gcal import get_upcoming_events


app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

def run_meeting_loop(update_status=None, update_next_meeting=None):
    try:
        while True:
            now = datetime.now(timezone.utc)
            seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000
            events = get_upcoming_events()

            if not events:
                print("No upcoming events found.")
                if update_status:
                    update_status("No upcoming events")
                time.sleep(seconds_to_next_minute)
                continue

            event = events[0]
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            start_time = datetime.fromisoformat(start_str).astimezone(timezone.utc)
            end_time = datetime.fromisoformat(end_str).astimezone(timezone.utc)
            seconds_until_start = (start_time - now).total_seconds()

            if update_next_meeting:
                update_next_meeting(start_time)

            print("Seconds until start:", seconds_until_start)
            status = ""

            if seconds_until_start > 600:
                status = "Idle"
                print("Meeting is more than 10 minutes away. Turning to normal.")
                set_color_temperature(2900)
                set_light_brightness(10)
            elif 60 < seconds_until_start <= 600:
                status = "Meeting soon"
                print("Meeting is within 10 minutes. Setting light to BLUE.")
                set_light_color(0, 0, 255)
                set_light_brightness(50)
            elif 0 < seconds_until_start <= 60:
                status = "Meeting imminent"
                print("Meeting is in less than 1 minute. Setting light to RED.")
                set_light_color(255, 0, 0)
                set_light_brightness(100)
            elif start_time <= now <= end_time:
                status = "In meeting"
                print("Meeting is ongoing. Setting light to WHITE.")
                set_light_color(255, 255, 255)
                set_light_brightness(50)
            else:
                status = "Idle"
                print("Meeting has ended. Turning to normal.")
                set_color_temperature(2900)
                set_light_brightness(10)

            if update_status:
                update_status(status)

            print(f"waiting {seconds_to_next_minute} seconds until next check...")
            time.sleep(seconds_to_next_minute)

    except KeyboardInterrupt:
        print("\nMeeting light loop stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        set_light_off()
        print("Light turned off due to error.")