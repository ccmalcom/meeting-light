import os
import subprocess
from dotenv import load_dotenv

# Ensure App Support directory exists and load .env from there
app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
os.makedirs(app_support_path, exist_ok=True)
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

required_env_vars = [
    "GOVEE_API_KEY",
    "GOVEE_DEVICE_MAC",
    "GOVEE_MODEL",
    "GOOGLE_API_KEY",
    "GOOGLE_CALENDAR_ID"
]


if not all(os.getenv(var) for var in required_env_vars):
    print("Missing environment variables. Launching setup in Terminal...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    apple_script = f'''
    tell application "Terminal"
        activate
        do script "cd '{base_path}' && source .venv/bin/activate && python setup.py"
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script])
    exit()
import rumps
import threading
from datetime import datetime
from main import run_meeting_loop
from govee import set_light_color

class MeetingLightApp(rumps.App):
    def __init__(self):
        super().__init__("💡 Meeting Light", quit_button="Quit")
        self.status_item = rumps.MenuItem("Status: Initializing...")
        self.next_meeting_item = rumps.MenuItem("Next Meeting At: Unknown")
        self.test_light_item = rumps.MenuItem("Test Light (set green)", callback=self.test_light)

        self.menu = [
            self.status_item,
            self.next_meeting_item,
            None,  # separator
            self.test_light_item
        ]

        self.update_thread = threading.Thread(target=self.run_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def run_loop(self):
        def update_status(status):
            self.status_item.title = f"Status: {status}"

        def update_next_meeting(start_time: datetime):
            local_time = start_time.astimezone().strftime("%I:%M %p")
            self.next_meeting_item.title = f"Next Meeting At: {local_time}"

        run_meeting_loop(update_status=update_status, update_next_meeting=update_next_meeting)

    def test_light(self, _):
        set_light_color(0, 255, 128)

if __name__ == "__main__":
    MeetingLightApp().run()