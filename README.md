# 💡 Meeting Light

> Never miss a meeting. A smart macOS menubar app that uses your Govee LED light to give you visual notifications for upcoming calendar events.

**Meeting Light** monitors your Google Calendar and automatically controls your Govee LED light to keep you aware of your schedule - even when you're away from your screen.

[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ v1.1.0 Features

### 🎨 Visual Notifications
- **🟡 Warm White (Idle)**: Meeting is more than 10 minutes away
- **🔵 Blue (Soon)**: Meeting starts in 10 minutes  
- **🔴 Red (Imminent)**: Meeting starts in 1 minute
- **⚪ White (Active)**: Currently in a meeting

### 🚀 Smart & Reliable
- **Intelligent State Tracking**: Reduces API calls by 97% - only changes light when needed
- **Robust Connection Handling**: Automatic retry with exponential backoff
- **Sleep/Wake Resilient**: Recovers automatically after laptop sleep
- **Health Monitoring**: Periodic connection health checks with auto-recovery
- **Smart Meeting Filtering**: Automatically ignores declined, cancelled, and all-day events

### 🎛️ User-Friendly
- **Menubar Integration**: Lives in your macOS menubar - always accessible
- **Live Status**: See your meeting status at a glance
- **Next Meeting Info**: Shows when your next meeting starts
- **Test Function**: Test your light anytime with one click
- **Easy Configuration**: Simple settings interface

### 📊 Advanced Features
- **Comprehensive Logging**: All events logged to file for troubleshooting
- **Rate Limit Protection**: Respects API limits automatically
- **Error Recovery**: Graceful handling of network issues and API errors
- **Customizable**: Easy configuration via centralized config file

---

## 🚀 Quick Start

### Installation

1. **Download the app**
   
   Download the latest `.zip` release from the [Releases](https://github.com/ccmalcom/meeting-light/releases) page and unzip it.

2. **Install**
   
   Move `Meeting Light.app` to your `/Applications` folder.

3. **First Launch Setup**
   
   On first launch, you'll be prompted to enter:
   
   - **Govee API Key**: Get yours at [developer.govee.com](https://developer.govee.com)
   - **Govee Device MAC**: Found in the Govee app under device settings (format: `XX:XX:XX:XX:XX:XX`)
   - **Govee Model**: Your device model (e.g., `H6159`, `H6076`)
   - **Google Calendar ID**: Usually your email address (find it in Google Calendar Settings → Integrate calendar)

4. **Launch**
   
   Look for the 💡 icon in your menubar!

### Auto-Start at Login (Optional)

Go to **System Settings > General > Login Items** and add Meeting Light.

---

## 💻 Usage

### Menubar Controls

Click the 💡 icon to access:
- **Status**: Current meeting status
- **Next Meeting**: Time of your next meeting
- **Test Light**: Verify your light is working (sets to green)
- **Settings**: Update your configuration
- **Quit**: Exit the app

### What the Colors Mean

| Light Color               | Status     | Meaning                  |
| ------------------------- | ---------- | ------------------------ |
| 🟡 Warm White (2900K, 10%) | Idle       | Meeting >10 minutes away |
| 🔵 Blue (50%)              | Soon       | Meeting in 10 minutes    |
| 🔴 Red (100%)              | Imminent   | Meeting in <1 minute     |
| ⚪ White (50%)             | In Meeting | Meeting in progress      |

### Logs

View detailed logs for troubleshooting:
```bash
tail -f ~/Library/Application\ Support/MeetingLight/meetinglight.log
```

Or open the log file:
```bash
open ~/Library/Application\ Support/MeetingLight/meetinglight.log
```

---

## ⚙️ Customization

Want to customize the behavior? Edit the `config.py` file in your project directory:

### Change Timing Thresholds
```python
MEETING_IDLE_THRESHOLD = 900  # Blue light 15 min before (default: 600)
MEETING_SOON_THRESHOLD = 30   # Red light 30 sec before (default: 60)
```

### Change Colors
```python
COLOR_SOON = (255, 255, 0)      # Yellow instead of blue
COLOR_IMMINENT = (255, 165, 0)  # Orange instead of red
```

### Change Brightness
```python
BRIGHTNESS_SOON = 75      # Brighter blue (default: 50)
BRIGHTNESS_IMMINENT = 100 # Max brightness (default: 100)
```

### Change Health Check Interval
```python
HEALTH_CHECK_INTERVAL = 600  # Check every 10 minutes (default: 300)
```

After editing, rebuild the app:
```bash
python setup.py py2app
mv dist/Meeting\ Light.app /Applications/
```

---

## 🛠️ Development

### Prerequisites

- macOS 10.14+
- Python 3.9 or higher
- A Govee light with API access
- A Google Calendar (public or with API access)

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/ccmalcom/meeting-light.git
   cd meeting-light
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Create `.env` file in `~/Library/Application Support/MeetingLight/`:
   ```bash
   GOVEE_API_KEY=your_key_here
   GOVEE_DEVICE_MAC=XX:XX:XX:XX:XX:XX
   GOVEE_MODEL=H6159
   GOOGLE_CALENDAR_ID=your_email@gmail.com
   ```

4. **Run directly**
   ```bash
   python app.py
   ```

### Building the App

Build a standalone application:
```bash
# Development build (faster, for testing)
python setup.py py2app -A

# Production build (standalone)
python setup.py py2app
```

The app will be in the `dist/` folder.

### Project Structure

```
meeting-light/
├── config.py           # Centralized configuration
├── main.py            # Main event loop logic
├── govee.py           # Govee LED API integration
├── gcal.py            # Google Calendar API integration
├── app.py             # macOS menubar app interface
├── setup.py           # py2app build configuration
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## 📋 Requirements

### Hardware
- Compatible Govee LED light with API support
  - Tested models: H6159, H6076, H6001
  - See [Govee API docs](https://developer.govee.com) for full list

### Software
- macOS 10.14 (Mojave) or newer
- Python 3.9+ (for development only)

### API Access
- Govee Developer API key (free)
- Google Calendar API access (free for public calendars)

### Python Dependencies
See [`requirements.txt`](requirements.txt) for the complete list. Key dependencies include:
- `rumps` - macOS menubar app framework
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `google-api-python-client` - Google Calendar integration

---

## 🔧 Troubleshooting

### Light Not Responding

1. **Check logs** for specific errors:
   ```bash
   tail -f ~/Library/Application\ Support/MeetingLight/meetinglight.log
   ```

2. **Verify credentials** in Settings menu

3. **Test with Govee app** - Can you control the light from the official app?

4. **Check Wi-Fi** - Both your Mac and light must be on the same network

5. **Restart the app**

### After Sleep/Wake Issues

The app automatically handles sleep/wake cycles. If issues persist:
1. Check the logs for recovery attempts
2. Restart the app
3. The next health check (every 5 minutes) will attempt recovery

### Calendar Not Updating

1. Verify your `GOOGLE_CALENDAR_ID` is correct
2. Check that the calendar is public or you have API access
3. Look for authentication errors in the logs

### Common Error Messages

| Error                   | Solution                                               |
| ----------------------- | ------------------------------------------------------ |
| "Authentication failed" | Check your Govee API key in Settings                   |
| "Calendar not found"    | Verify your Google Calendar ID                         |
| "Connection timeout"    | Check your internet connection                         |
| "Rate limited"          | Wait a few minutes, the app handles this automatically |

---

## 📊 Technical Details

### Architecture

Meeting Light uses a polling architecture:
1. **Calendar Polling**: Checks Google Calendar every 60 seconds
2. **Health Checks**: Verifies connection every 5 minutes
3. **State Tracking**: Only sends API calls when light state needs to change
4. **Retry Logic**: Automatic retry with exponential backoff on failures

### API Call Optimization

The app uses intelligent state tracking to minimize API calls:
- **Without optimization**: ~960 API calls per 8-hour day
- **With optimization**: ~24 API calls per 8-hour day
- **Reduction**: 97.5%

This prevents rate limiting and improves performance.

### Connection Resilience

- Automatic retry (up to 3 attempts) with exponential backoff
- Timeout protection (10 seconds)
- Connection health monitoring
- Sleep/wake cycle recovery
- Rate limit handling

### Privacy & Security

- All credentials stored locally in `~/.env`
- No data sent to third parties
- Only communicates with Govee and Google APIs
- Logs stored locally on your machine

---

## 🎯 Roadmap

Future enhancements under consideration:
- [ ] Full UI for customization
- [ ] Multiple calendar support
- [ ] Custom color schemes per meeting type
- [ ] Meeting category filtering
- [ ] Multiple light support
- [ ] Notification sounds
- [ ] Focus mode integration
- [ ] Meeting duration display
- [ ] Dark mode menubar icon

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. Follow Python best practices (PEP 8)
2. Add type hints to all functions
3. Include docstrings
4. Update tests if applicable
5. Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Powered By

- [Google Calendar API](https://developers.google.com/calendar) - Calendar integration
- [Govee Developer API](https://developer.govee.com/) - LED light control
- [rumps](https://github.com/jaredks/rumps) - macOS menubar app framework

### Inspiration

Built for remote workers who need visual cues for upcoming meetings without constant screen checking.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ccmalcom/meeting-light/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ccmalcom/meeting-light/discussions)

---

<div align="center">

**Made with ❤️ for remote workers**

If you find this useful, consider ⭐ starring the repo!

</div>