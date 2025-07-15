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