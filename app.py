import os
import sys
from dotenv import load_dotenv, set_key, dotenv_values

# Ensure App Support directory exists and load .env from there
app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
os.makedirs(app_support_path, exist_ok=True)
env_path = os.path.join(app_support_path, ".env")

if not os.path.exists(env_path):
    with open(env_path, "w") as f:
        f.write("")  # Create an empty .env file if it doesn't exist

# Load current env values
existing_env = dotenv_values(env_path)

# Set a default Google API key if it's not already set
DEFAULT_GOOGLE_API_KEY = "AIzaSyA-wjjty7da5rKr_gEm6OJna4vm_X9XGoo"
if "GOOGLE_API_KEY" not in existing_env:
    set_key(env_path, "GOOGLE_API_KEY", DEFAULT_GOOGLE_API_KEY)

load_dotenv(dotenv_path=env_path)

required_env_vars = [
    "GOVEE_API_KEY",
    "GOVEE_DEVICE_MAC",
    "GOVEE_MODEL",
    "GOOGLE_API_KEY",
    "GOOGLE_CALENDAR_ID"
]

import rumps
import threading
from datetime import datetime
from main import run_meeting_loop
from govee import set_light_color

class MeetingLightApp(rumps.App):
    def __init__(self):
        super().__init__("💡", quit_button="Quit")
        self.status_item = rumps.MenuItem("Status: Initializing...")
        self.next_meeting_item = rumps.MenuItem("Next Meeting At: Unknown")
        self.test_light_item = rumps.MenuItem("Test Light (set green)", callback=self.test_light)
        self.settings_item = rumps.MenuItem("Settings", callback=self.open_settings)

        self.menu = [
            self.status_item,
            self.next_meeting_item,
            None,  # separator
            self.test_light_item,
            self.settings_item,
        ]

        # Prompt for missing env vars on first launch
        if not all(os.getenv(var) for var in required_env_vars):
            rumps.alert("Welcome to Meeting Light!\n\nPlease enter your configuration values on the next screens.\n\nYou can change these later in the Settings menu. For more information, please see the README.md file.")
            self.open_settings(None)
            load_dotenv(dotenv_path=env_path, override=True)

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
        
    def open_settings(self, _):

        config = dotenv_values(env_path)

        fields = {
            "GOVEE_API_KEY": "Enter your Govee API Key:",
            "GOVEE_DEVICE_MAC": "Enter your Govee Device MAC:",
            "GOVEE_MODEL": "Enter your Govee Model:",
            "GOOGLE_CALENDAR_ID": "Enter your Google Calendar ID:"
        }

        for key, message in fields.items():
            current_value = config.get(key, "")
            response = rumps.Window(
                message=message,
                default_text=current_value,
                title="settings",
                ok="Save",
                cancel="Skip"
            ).run()

            if response.clicked and response.text:
                set_key(env_path, key, response.text)

        rumps.alert("Config updated! Restarting the app...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
if __name__ == "__main__":
    MeetingLightApp().run()