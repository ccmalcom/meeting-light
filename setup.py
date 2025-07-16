from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'packages': ['rumps', 'dotenv', 'requests'],
    'includes': ['dotenv', 'imp'],
    'excludes': ['tkinter', 'Tcl', 'Tk'],
    'plist': {
        'CFBundleName': 'Meeting Light',
        'CFBundleDisplayName': 'Meeting Light',
        'CFBundleIdentifier': 'com.chasemalcom.meetinglight',
        'CFBundleVersion': '1.0.0',
        'LSUIElement': True,  # Hides from Dock, makes it a menubar app
    },
    'iconfile': 'MeetingLight.icns', 
}

setup(
    app=APP,
    name='Meeting Light',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'setuptools<81'],
    install_requires=[
        'rumps',
        'python-dotenv',
        'requests',
    ],
)