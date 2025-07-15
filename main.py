from govee import set_light_on, set_light_off, get_device_list, set_light_color, set_light_brightness, set_color_temperature
from gcal import get_upcoming_events
from datetime import datetime, timezone
import time

try:
    while True:
        now = datetime.now(timezone.utc)
        seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000
        events = get_upcoming_events()
        if not events:
            print("No upcoming events found.")
            # set_light_off()
            time.sleep(seconds_to_next_minute)
            continue

        event = events[0]
        start_str = event['start'].get('dateTime')
        end_str = event['end'].get('dateTime')

        print("Start:", start_str)
        print("End:", end_str)

        start_time = datetime.fromisoformat(start_str).astimezone(timezone.utc)
        end_time = datetime.fromisoformat(end_str).astimezone(timezone.utc)

        seconds_until_start = (start_time - now).total_seconds()
        print("Seconds until start:", seconds_until_start)

        if seconds_until_start > 600:
            print("Meeting is more than 10 minutes away. Turning to normal.")
            set_color_temperature(2900)  # Set to normal color temperature
        elif 60 < seconds_until_start <= 600:
            print("Meeting is within 10 minutes. Setting light to BLUE.")
            set_light_color(0, 0, 255)  # Blue
        elif 0 < seconds_until_start <= 60:
            print("Meeting is in less than 1 minute. Setting light to RED.")
            set_light_color(255, 0, 0)  # Red
        elif start_time <= now <= end_time:
            print("Meeting is ongoing. Setting light to WHITE.")
            set_light_color(255, 255, 255)  # White
        else:
            print("Meeting has ended. Turning off light.")
            set_color_temperature(2900)  # Set to normal color temperature
        print(f"waiting {seconds_to_next_minute} seconds until next check...")
        time.sleep(seconds_to_next_minute)

except KeyboardInterrupt:
    print("\nMeeting light loop stopped by user.")
    
