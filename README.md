# LinkedIn Easy Apply Bot

This application is a Python bot with a graphical interface for automating job applications on [LinkedIn Jobs](https://www.linkedin.com/jobs/).

## Features
- Modern GUI (Tkinter + ttkthemes)
- Start/stop bot and browser independently
- Edit and save filters (badWords, titleFilterWords, titleSkipWords) in a convenient UI
- Autofill forms for "Easy Apply" jobs, including text, radio, and dropdown fields
- Automatically adds new form fields/questions to the database for later user input
- Uses your own Chrome profile for persistent login
- Inspired by a working Chrome extension (see `.cursor/example_from_chrome_ext`)

## Quick Start
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure browser path:**
   - Open the app, go to the "Browser" tab, and set the path to your Chrome executable.
3. **Edit filters and autofill:**
   - Use the "Filters" and "Autofill" tabs to set your preferences and personal data.
4. **Open browser:**
   - Click "Open Browser" to launch Chrome with your profile.
5. **Start bot:**
   - Click "Start" to begin automated job applications. Use "Stop" to pause/resume on the current page.

## Dependencies
- Python 3.9+
- selenium>=4.15.0
- webdriver-manager>=4.0.0
- beautifulsoup4>=4.12.0
- jsonschema>=4.19.0
- python-dotenv>=1.0.0
- ttkthemes>=3.2.2
- watchdog>=6.0.0

## How it works
- The bot navigates to LinkedIn Jobs, applies filters, and iterates through job listings.
- Only "Easy Apply" jobs are processed; forms are filled using your saved data.
- If a new question/field is encountered, it is added to the database for you to fill in later.
- All user data and settings are stored in the `DB/` folder as JSON files.

## Notes
- All UI and user-facing text is in English.
- The bot is designed for educational and personal productivity use only. Use responsibly and in accordance with LinkedIn's terms of service. 