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

#### 1. Download the app

Download the latest `.zip` release from the [Releases](https://github.com/ccmalcom/meeting-light/releases) page and unzip it.

Move `Meeting Light.app` to your `/Applications` folder.

#### 2. First launch setup

On first launch, the app will prompt you to enter the following credentials, which will be saved in a `.env` file in `~/Library/Application Support/MeetingLight`:

- **Govee API Key**: You can request your personal API key by signing into your Govee account at [https://developer.govee.com](https://developer.govee.com) and registering for API access.
- **Govee MAC Address**: This is the unique identifier for your Govee device. You can find it in the Govee app under the device's settings.
- **Govee Model (e.g. H6159)**: The model number of your Govee light. It’s listed in the app or on the packaging.
- **Google Calendar ID**: Use the ID of a public Google Calendar you want to sync. This is usually your email address or a custom calendar ID (found in Google Calendar settings under “Integrate calendar”).

---

### 💻 Usage

#### Running the App

Double-click `Meeting Light.app` to launch it from your Applications folder. It will run in your macOS menubar.

To enable the app to launch at login, go to **System Settings > General > Login Items** and add Meeting Light.

---

### 🛠 Requirements

- Python 3.9+ (only for development)
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