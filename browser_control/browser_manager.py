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
from .easy_apply__job import apply_to_job
import re

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

    def go_to_url(self, url):
        if self.driver:
            self.driver.get(url)
    def process_job_listings(self, autofill_path, filters_path=None, should_continue=lambda: True):
        if not self.driver:
            print("No driver")
            return False
        try:
            with open(autofill_path, "r", encoding="utf-8") as f:
                autofill_data = json.load(f)
            filters = {}
            if filters_path:
                try:
                    with open(filters_path, "r", encoding="utf-8") as f:
                        filters = json.load(f)
                except Exception:
                    filters = {}
            wait = WebDriverWait(self.driver, 20)
            time.sleep(2)
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".scaffold-layout__list-item")
            title_filter_words = [w.lower() for w in filters.get("titleFilterWords", [])]
            title_skip_words = [w.lower() for w in filters.get("titleSkipWords", [])]
            bad_words = [w.lower() for w in filters.get("badWords", [])]
            filtered_jobs = []
            for idx, job_card in enumerate(job_cards):
                if not should_continue():
                    print("Bot stopped by user during filtering.")
                    return
                try:
                    try:
                        job_title_el = job_card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title .job-card-container__link")
                    except Exception:
                        try:
                            job_title_el = job_card.find_element(By.CSS_SELECTOR, ".job-card-container__link")
                        except Exception:
                            continue
                    job_title = job_title_el.text.strip().lower()
                    subtitle = ""
                    try:
                        subtitle = job_card.find_element(By.CSS_SELECTOR, '[class*="subtitle"]').text.strip().lower()
                    except Exception:
                        pass
                    # Проверка titleSkipWords по целым словам
                    if any(re.search(r'\b' + re.escape(skip) + r'\b', job_title) or re.search(r'\b' + re.escape(skip) + r'\b', subtitle) for skip in title_skip_words):
                        continue
                    # Проверка titleFilterWords по целым словам
                    if title_filter_words and not any(re.search(r'\b' + re.escape(f) + r'\b', job_title) for f in title_filter_words):
                        continue
                    filtered_jobs.append((job_card, job_title_el))
                except Exception as e:
                    print(f"Error filtering job {idx}: {e}")
            for job_card, job_title_el in filtered_jobs:
                if not should_continue():
                    print("Bot stopped by user during job processing.")
                    return
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
                    time.sleep(0.5)
                    job_title_el.click()
                    time.sleep(2)
                    try:
                        job_details = self.driver.find_element(By.CSS_SELECTOR, '[class*="jobs-box__html-content"]').text.lower()
                        # Проверка badWords по целым словам
                        if any(re.search(r'\b' + re.escape(bad) + r'\b', job_details) for bad in bad_words):
                            continue
                    except Exception:
                        pass
                    apply_to_job(self.driver, autofill_data)
                except Exception as e:
                    print(f"Error processing filtered job: {e}")
            try:
                scroll_container = self.driver.find_element(By.CSS_SELECTOR, ".scaffold-layout__list > div")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_container)
                time.sleep(1)
            except Exception:
                pass
            try:
                if not should_continue():
                    print("Bot stopped by user before next page.")
                    return
                next_btn = self.driver.find_element(By.CSS_SELECTOR, 'button.jobs-search-pagination__button--next[aria-label*="next"]:not([disabled])')
                if next_btn:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(1)
                    next_btn.click()
                    time.sleep(3)
                    self.process_job_listings(autofill_path, filters_path, should_continue)
            except Exception as e:
                print(f"No more pages or next button not found. Finished. {e}")
        except Exception as e:
            print("Error in process_job_listings:", e)
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