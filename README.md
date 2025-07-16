

# 💡 Meeting Light

**Meeting Light** is a lightweight macOS menubar app that uses a Govee LED light bar to visually notify you of upcoming meetings pulled from your Google Calendar.

### ✨ Features

- Blue light 10 minutes before a meeting
- Red light 1 minute before a meeting
- Warm white light during a meeting
- Automatic light reset after meeting
- Menubar app with live status, next meeting info, and a test light button

---

### 🚀 Setup

#### 1. Clone this repo

```bash
git clone https://github.com/yourusername/meeting-light.git
cd meeting-light
```

#### 2. Run the setup script

```bash
python setup.py
```

You’ll be prompted to enter:

- Govee API Key
- Govee MAC Address
- Govee Model (e.g. H6159)
- Google Calendar API Key
- Google Calendar ID

These will be saved in a `.env` file in ~/Library/Application Support/MeetingLight.

---

### 💻 Usage

#### Development mode:

```bash
source .venv/bin/activate
python app.py
```

To run the app as a background utility at login, you can create a macOS Automator app or use tools like `rumps` to generate a menubar app.

---

### 🛠 Requirements

- Python 3.9+
- A Govee light device with API access
- A public Google Calendar
- Dependencies: see `requirements.txt`

---

### 📸 Screenshot

![screenshot-placeholder](https://via.placeholder.com/300x100?text=Screenshot+Coming+Soon)

---

### 🧠 Powered by

- [Google Calendar API](https://developers.google.com/calendar)
- [Govee Developer API](https://developer.govee.com/)
- [rumps (Ridiculously Uncomplicated Mac Python Statusbar apps)](https://github.com/jaredks/rumps)

---
MIT License