from selenium.webdriver.chrome.options import Options


class ChromeOptionsBuilder:
    @staticmethod
    def build_options(executable_path, user_data_dir, profile_directory="Default"):
        """Create and configure Chrome options for automation."""
        chrome_options = Options()
        
        # Set Chrome executable path
        chrome_options.binary_location = executable_path
        
        # Configure user profile
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={profile_directory}")
        
        # Anti-detection settings
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        return chrome_options

    @staticmethod
    def get_anti_detection_script():
        """Get JavaScript to execute for additional anti-detection."""
        return "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"

    @staticmethod
    def add_headless_options(chrome_options):
        """Add headless mode options to existing chrome_options."""
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        return chrome_options

    @staticmethod
    def add_performance_options(chrome_options):
        """Add performance optimization options."""
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        return chrome_options

    @staticmethod
    def add_window_options(chrome_options, width=1920, height=1080):
        """Add window size options."""
        chrome_options.add_argument(f"--window-size={width},{height}")
        return chrome_options