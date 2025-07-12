import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

linkedin_url = "https://www.linkedin.com/jobs/"

PROFILE_DIR = Path(__file__).parent.parent / "chrome_profile"
PROFILE_DEFAULT = PROFILE_DIR / "Default"

class BrowserManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.driver = None
        self.ensure_profile_dir()

    def ensure_profile_dir(self):
        PROFILE_DEFAULT.mkdir(parents=True, exist_ok=True)
        gitkeep = PROFILE_DIR / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

    def start_browser(self):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            executable_path = data.get("executable_path", "")
            if not os.path.exists(executable_path):
                raise FileNotFoundError("Browser executable path not found.")
            user_data_dir = str(PROFILE_DIR)
            profile_directory = "Default"
            chrome_options = Options()
            chrome_options.binary_location = executable_path
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile_directory}")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            return True
        except Exception as e:
            self.driver = None
            raise e

    def go_to_url(self, url=linkedin_url):
        if self.driver:
            self.driver.get(url)

    def fill_job_search_and_submit(self, autofill_path):
        if not self.driver:
            print("No driver")
            return False
        try:
            with open(autofill_path, "r", encoding="utf-8") as f:
                autofill_data = json.load(f)
            job_title = autofill_data.get("inputFieldConfigs", {}).get("jobTitle", "")
            print("job_title:", job_title)
            if not job_title:
                return False
            wait = WebDriverWait(self.driver, 20)
            # Ищем по aria-label, так как id может меняться
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")))
            print("search_input found:", search_input)
            search_input.clear()
            search_input.send_keys(job_title)
            search_input.send_keys(Keys.ENTER)
            return True
        except Exception as e:
            print("Error in fill_job_search_and_submit:", e)
            return False

    def stop(self):
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception:
            self.driver = None

    def is_running(self):
        return self.driver is not None 