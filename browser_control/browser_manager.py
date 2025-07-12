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

# 1. Переименовать linkedin_url в job_apply_url
# 2. Убрать fill_job_search_and_submit
# 3. Получать job_apply_url из базы и сразу переходить по нему
job_apply_url = "https://www.linkedin.com/jobs/"

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

    def go_to_url(self, url=job_apply_url):
        if self.driver:
            self.driver.get(url)

    # 2. Убрать fill_job_search_and_submit
    # def fill_job_search_and_submit(self, autofill_path):
    #     if not self.driver:
    #         print("No driver")
    #         return False
    #     try:
    #         with open(autofill_path, "r", encoding="utf-8") as f:
    #             autofill_data = json.load(f)
    #         job_title = autofill_data.get("inputFieldConfigs", {}).get("jobTitle", "")
    #         print("job_title:", job_title)
    #         if not job_title:
    #             return False
    #         wait = WebDriverWait(self.driver, 20)
    #         # Ищем по aria-label, так как id может меняться
    #         search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")))
    #         print("search_input found:", search_input)
    #         search_input.clear()
    #         search_input.send_keys(job_title)
    #         search_input.send_keys(Keys.ENTER)
    #         return True
    #     except Exception as e:
    #         print("Error in fill_job_search_and_submit:", e)
    #         return False

    def process_job_listings(self, autofill_path, filters_path=None):
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
            # 1. Собрать titleFilterWords и titleSkipWords
            title_filter_words = [w.lower() for w in filters.get("titleFilterWords", [])]
            title_skip_words = [w.lower() for w in filters.get("titleSkipWords", [])]
            bad_words = [w.lower() for w in filters.get("badWords", [])]
            filtered_jobs = []
            for idx, job_card in enumerate(job_cards):
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
                    # 2. Фильтрация по titleSkipWords
                    if any(skip in job_title or skip in subtitle for skip in title_skip_words):
                        continue
                    # 3. Фильтрация по titleFilterWords
                    if title_filter_words and not any(f in job_title for f in title_filter_words):
                        continue
                    filtered_jobs.append((job_card, job_title_el))
                except Exception as e:
                    print(f"Error filtering job {idx}: {e}")
            # 4. Скроллинг списка (делаем scrollIntoView для каждого)
            for job_card, job_title_el in filtered_jobs:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
                    time.sleep(0.5)
                    job_title_el.click()
                    time.sleep(2)
                    # После клика — проверка badWords
                    try:
                        job_details = self.driver.find_element(By.CSS_SELECTOR, '[class*="jobs-box__html-content"]').text.lower()
                        if any(bad in job_details for bad in bad_words):
                            continue
                    except Exception:
                        pass
                    # Easy Apply обработка
                    apply_to_job(self.driver, autofill_data)
                except Exception as e:
                    print(f"Error processing filtered job: {e}")
            # 5. Скроллинг вниз перед поиском Next
            try:
                scroll_container = self.driver.find_element(By.CSS_SELECTOR, ".scaffold-layout__list > div")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_container)
                time.sleep(1)
            except Exception:
                pass
            # 6. Переход к следующей странице
            try:
                # Новый селектор для Next
                next_btn = self.driver.find_element(By.CSS_SELECTOR, 'button.jobs-search-pagination__button--next[aria-label*="next"]:not([disabled])')
                if next_btn:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(1)
                    next_btn.click()
                    time.sleep(3)
                    self.process_job_listings(autofill_path, filters_path)
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