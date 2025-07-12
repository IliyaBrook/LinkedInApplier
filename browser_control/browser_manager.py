import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

linkedin_url = "https://www.linkedin.com/feed/"

class BrowserManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.driver = None

    def start(self, url=linkedin_url):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            executable_path = data.get("executable_path", "")
            profile_path = data.get("profile_path", "")
            if not os.path.exists(executable_path):
                raise FileNotFoundError("Browser executable path not found.")
            if not os.path.exists(profile_path):
                raise FileNotFoundError("Browser profile path not found.")
            user_data_dir = os.path.dirname(profile_path)
            profile_directory = os.path.basename(profile_path)
            chrome_options = Options()
            chrome_options.binary_location = executable_path
            # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            # chrome_options.add_argument(f"--profile-directory={profile_directory}")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.driver.get(url)
            return True
        except Exception as e:
            self.driver = None
            raise e

    def stop(self):
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception:
            self.driver = None

    def is_running(self):
        return self.driver is not None 