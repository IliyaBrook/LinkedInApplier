# LinkedIn Easy Apply Bot - Developer Guidelines

## Project Overview
This is a Python-based LinkedIn job application automation tool with a modern Tkinter GUI. The bot uses Selenium WebDriver to automate the "Easy Apply" process on LinkedIn Jobs.

## Tech Stack
- **Python**: 3.9+ required
- **GUI Framework**: Tkinter with ttkthemes for modern styling
- **Web Automation**: Selenium WebDriver with Chrome
- **Data Storage**: JSON files for configuration and user data
- **Code Formatting**: Black (line length: 88)
- **Development Tools**: debugpy for debugging, watchdog for file monitoring

## Project Structure
```
LinkedInApplier/
├── main.py                 # Application entry point
├── ui/                     # User interface modules
│   ├── main_ui.py         # Main application window
│   ├── autofill_tab.py    # Form autofill configuration
│   ├── browser_tab.py     # Browser settings
│   └── filters_tab.py     # Job filtering options
├── browser_control/        # Web automation logic
│   ├── browser_manager.py # Main browser controller
│   ├── easy_apply__job.py # Job application logic
│   └── browser_utils/     # Utility functions
├── DB/                    # JSON configuration files
│   ├── user_filters.json # Job filtering criteria
│   ├── form_autofill.json # Autofill form data
│   └── browser_settings.json # Browser configuration
├── chrome_profile/        # Chrome user profile data
└── cheatsheets/          # Documentation and examples
```

## Quick Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **For development with auto-reload**:
   ```bash
   python run_with_reload.py
   ```

## Development Guidelines

### Code Style
- Use **Black** formatter with 88-character line length
- Format code before committing: `black .`
- Follow PEP 8 naming conventions
- Add docstrings for classes and complex functions

### File Organization
- **UI components**: Place in `ui/` directory, one tab per file
- **Browser automation**: Add to `browser_control/` or `browser_control/browser_utils/`
- **Configuration**: Store in `DB/` as JSON files
- **Documentation**: Add to `cheatsheets/` directory

### Adding New Features
1. **UI changes**: Modify appropriate tab file in `ui/`
2. **Automation logic**: Add to `browser_control/` modules
3. **Configuration**: Update corresponding JSON schema and files
4. **Utilities**: Place reusable functions in `browser_utils/`

### Testing Guidelines
⚠️ **IMPORTANT**: Do NOT create test files in this project directory. This project does not use automated testing frameworks. Instead:
- Test manually through the GUI
- Use the browser automation features to verify functionality
- Test with real LinkedIn pages in a controlled manner
- Document any manual testing procedures in `cheatsheets/`

### Best Practices
- **Error Handling**: Use try-catch blocks for Selenium operations
- **Logging**: Use print statements for user feedback (no formal logging yet)
- **Delays**: Add appropriate `time.sleep()` calls to avoid rate limiting
- **Chrome Profile**: Leverage persistent Chrome profile for login state
- **JSON Validation**: Validate JSON files before processing
- **Graceful Shutdown**: Ensure browser cleanup in error scenarios

### Common Patterns
- **Element Finding**: Use WebDriverWait with expected conditions
- **Modal Handling**: Check `browser_utils/` for existing modal handlers
- **Scrolling**: Use existing scroll utilities for consistent behavior
- **Form Filling**: Follow patterns in `easy_apply__job.py`

### Configuration Management
- All user settings stored in `DB/` as JSON files
- Settings are loaded at runtime and can be modified through UI
- New form fields are automatically added to database for user completion
- Browser settings include Chrome executable path and profile options

### Debugging
- Use `debugpy` for debugging (already included in requirements)
- Enable Chrome DevTools for web element inspection
- Check browser console for JavaScript errors
- Monitor network requests for LinkedIn API changes

## Running the Application
1. Configure browser path in the "Browser" tab
2. Set up filters and autofill data in respective tabs
3. Click "Open Browser" to launch Chrome with your profile
4. Navigate to LinkedIn Jobs manually
5. Click "Start" to begin automated applications
6. Use "Stop" to pause/resume on current page

## Important Notes
- **Educational Use**: This tool is for educational and personal productivity only
- **LinkedIn ToS**: Use responsibly and in accordance with LinkedIn's terms of service
- **Rate Limiting**: The bot includes delays to avoid overwhelming LinkedIn's servers
- **Profile Persistence**: Uses your Chrome profile for seamless login experience
- **Easy Apply Only**: Only processes jobs with "Easy Apply" button