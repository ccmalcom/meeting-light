from pathlib import Path
import os
import subprocess

print("🛠️  Meeting Light Setup Wizard\n")

govee_key = input("🔑 Enter your Govee API Key: ")
govee_mac = input("📟 Enter your Govee MAC address (e.g. AA:BB:CC:DD:EE:FF): ")
govee_model = input("💡 Enter your Govee model (e.g. H6159): ")

calendar_key = input("🗓️  Enter your Google Calendar API Key: ")
calendar_id = input("📅 Enter your Google Calendar ID: ")

env_content = f"""# Govee Device Settings
GOVEE_API_KEY={govee_key}
GOVEE_DEVICE_MAC={govee_mac}
GOVEE_MODEL={govee_model}

# Google Calendar Settings
GOOGLE_API_KEY={calendar_key}
GOOGLE_CALENDAR_ID={calendar_id}
"""

Path(".env").write_text(env_content.strip())

print("\n✅ Setup complete! Relaunching...")

# Relaunch app.py in a new Terminal window 

app_path = os.path.abspath("app.py")
apple_script = f'''
tell application "Terminal"
    activate
    do script "cd '{os.getcwd()}' && source .venv/bin/activate && open -a 'Meeting Light'"
end tell
'''

subprocess.run(["osascript", "-e", apple_script])

