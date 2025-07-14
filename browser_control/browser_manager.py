import json
import os
import re
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from .easy_apply__job import apply_to_job

PROFILE_DIR = Path(__file__).parent.parent / "chrome_profile"
PROFILE_DEFAULT = PROFILE_DIR / "Default"


class BrowserManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.driver = None
        self.ensure_profile_dir()

    @staticmethod
    def ensure_profile_dir():
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
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            return True
        except (FileNotFoundError, json.JSONDecodeError, OSError, WebDriverException) as e:
            print(f"Failed to start browser: {e}")
            return False

    def go_to_url(self, url):
        if self.driver:
            self.driver.get(url)

    def process_job_listings(
        self, autofill_path, filters_path=None, should_continue=lambda: True
    ):
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
                    print(f"DEBUG: Successfully loaded filters from {filters_path}")
                    print(
                        f"DEBUG: Raw titleSkipWords: {filters.get('titleSkipWords', [])}"
                    )
                except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
                    print(f"DEBUG: Failed to load filters: {e}")
                    filters = {}
            else:
                print("DEBUG: No filters_path provided")
            wait = WebDriverWait(self.driver, 20)
            time.sleep(2)
            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".scaffold-layout__list-item"
            )
            title_filter_words = [
                w.lower() for w in filters.get("titleFilterWords", [])
            ]
            title_skip_words = [w.lower() for w in filters.get("titleSkipWords", [])]
            bad_words = [w.lower() for w in filters.get("badWords", [])]

            print(f"Found {len(job_cards)} job cards on page")
            print(
                f"Filter settings: titleFilterWords={title_filter_words[:5]}{'...' if len(title_filter_words) > 5 else ''}, titleSkipWords={title_skip_words[:5]}{'...' if len(title_skip_words) > 5 else ''}, badWords={bad_words[:5]}{'...' if len(bad_words) > 5 else ''}"
            )
            print(f"DEBUG: Full titleSkipWords = {title_skip_words}")
            print(f"DEBUG: 'senior' in titleSkipWords = {'senior' in title_skip_words}")

            filtered_jobs = []
            for idx, job_card in enumerate(job_cards):
                if not should_continue():
                    print("Bot stopped by user during filtering.")
                    return None
                try:
                    print(f"\nProcessing job card {idx + 1}/{len(job_cards)}")
                    try:
                        applied_footer = job_card.find_element(
                            By.CSS_SELECTOR, ".job-card-container__footer-job-state"
                        )
                        footer_text = applied_footer.text.strip().lower()
                        if "applied" in footer_text:
                            print(
                                f"  Job {idx + 1}: Already applied (footer: '{footer_text}') - SKIPPING"
                            )
                            continue
                    except NoSuchElementException:
                        pass

                    try:
                        job_title_el = job_card.find_element(
                            By.CSS_SELECTOR,
                            ".artdeco-entity-lockup__title .job-card-container__link",
                        )
                        print(f"  DEBUG: Found job title element with first selector")
                    except NoSuchElementException:
                        try:
                            job_title_el = job_card.find_element(
                                By.CSS_SELECTOR, ".job-card-container__link"
                            )
                            print(
                                f"  DEBUG: Found job title element with second selector"
                            )
                        except NoSuchElementException:
                            print(
                                f"  Job {idx + 1}: No job title link found - SKIPPING"
                            )
                            continue

                    raw_title = job_title_el.text.strip()
                    aria_label = job_title_el.get_attribute("aria-label") or ""
                    job_title = raw_title.lower()
                    print(
                        f"  Job {idx + 1}: Raw title = '{raw_title}', Processed title = '{job_title}'"
                    )
                    print(f"  DEBUG: aria-label = '{aria_label}'")

                    subtitle = ""
                    try:
                        subtitle = (
                            job_card.find_element(
                                By.CSS_SELECTOR,
                                ".artdeco-entity-lockup__subtitle",
                            )
                            .text.strip()
                            .lower()
                        )
                        print(f"  Job {idx + 1}: Subtitle = '{subtitle}'")
                    except NoSuchElementException:
                        pass

                    # Check title filter words
                    if title_filter_words:
                        matched = any(
                            filter_word in job_title
                            for filter_word in title_filter_words
                        )
                        if not matched:
                            print(
                                f"  Job {idx + 1}: Title doesn't match filter words - SKIPPING"
                            )
                            continue
                        else:
                            print(f"  Job {idx + 1}: Title matches filter words - OK")
                    else:
                        print(f"  Job {idx + 1}: No title filter words - OK")

                    # Check title skip words
                    if title_skip_words:
                        print(
                            f"  DEBUG: Checking job title '{job_title}' against skip words {title_skip_words[:3]}..."
                        )
                        print(
                            f"  DEBUG: Job title length: {len(job_title)}, bytes: {job_title.encode('utf-8')}"
                        )
                        print(
                            f"  DEBUG: Looking for 'senior' specifically: {'senior' in job_title}"
                        )
                        skip = any(
                            skip_word in job_title for skip_word in title_skip_words
                        )
                        if skip:
                            # Find which skip word matched
                            matched_words = [
                                word for word in title_skip_words if word in job_title
                            ]
                            print(
                                f"  Job {idx + 1}: Title contains skip words {matched_words} - SKIPPING"
                            )
                            continue
                        else:
                            print(
                                f"  Job {idx + 1}: Title doesn't contain skip words - OK"
                            )
                    else:
                        print(f"  Job {idx + 1}: No title skip words - OK")

                    # Easy Apply button check will be done on job details page, not in job card
                    print(
                        f"  Job {idx + 1}: PASSED ALL FILTERS - Adding to filtered jobs"
                    )
                    # Store the original index along with the job card and title element
                    filtered_jobs.append((idx, job_card, job_title_el))
                except (NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
                    print(f"  Job {idx + 1}: Error filtering job: {e} - SKIPPING")

            print(
                f"\nFiltering complete: {len(filtered_jobs)} jobs passed filters out of {len(job_cards)} total jobs"
            )

            applied_count = 0
            for filter_idx, (original_idx, job_card, job_title_el) in enumerate(filtered_jobs):
                if not should_continue():
                    print("Bot stopped by user during job application.")
                    return None
                try:
                    print(f"\nApplying to filtered job {filter_idx + 1}/{len(filtered_jobs)} (original position {original_idx + 1})")

                    # Re-find job cards to avoid stale element reference
                    current_job_cards = self.driver.find_elements(
                        By.CSS_SELECTOR, ".scaffold-layout__list-item"
                    )

                    if original_idx >= len(current_job_cards):
                        print(
                            f"  Job {filter_idx + 1}: Job card no longer available at original position {original_idx + 1} - SKIPPING"
                        )
                        continue

                    current_job_card = current_job_cards[original_idx]

                    # Re-find a job title element
                    current_job_title_el = None
                    try:
                        current_job_title_el = current_job_card.find_element(
                            By.CSS_SELECTOR,
                            ".artdeco-entity-lockup__title .job-card-container__link",
                        )
                    except NoSuchElementException:
                        try:
                            current_job_title_el = current_job_card.find_element(
                                By.CSS_SELECTOR, ".job-card-container__link"
                            )
                        except NoSuchElementException:
                            print(
                                f"  Job {filter_idx + 1}: Could not re-find job title element - SKIPPING"
                            )
                            continue

                    time.sleep(0.5)

                    print(f"  Clicking on job title to open details...")
                    current_job_title_el.click()
                    time.sleep(2)

                    # Check badWords in job details
                    badwords_check_passed = True
                    try:
                        job_details = self.driver.find_element(
                            By.CSS_SELECTOR, '[class*="jobs-box__html-content"]'
                        ).text.lower()

                        if bad_words:  # Only check if the badWords array is not empty
                            if any(
                                re.search(r"\b" + re.escape(bad) + r"\b", job_details)
                                for bad in bad_words
                            ):
                                badwords_check_passed = False
                                print(f"  Job details contain bad words - SKIPPING")
                                continue
                            else:
                                print(f"  Job details don't contain bad words - OK")
                        else:
                            print(f"  No bad words filter - OK")
                    except (NoSuchElementException, WebDriverException) as e:
                        print(
                            f"  Could not check job details for bad words: {e} - Proceeding anyway"
                        )

                    if badwords_check_passed:
                        print(f"  Calling apply_to_job()...")
                        result = apply_to_job(self.driver, autofill_data)
                        print(f"  apply_to_job() returned: {result}")

                        if result:
                            applied_count += 1
                            print(
                                f"  Successfully applied! Total applications: {applied_count}"
                            )

                        # Small delay after application
                        time.sleep(1)

                except (NoSuchElementException, StaleElementReferenceException, WebDriverException, TimeoutException) as e:
                    print(f"  Error processing filtered job {filter_idx + 1}: {e}")

            print(f"\nCompleted job applications. Applied to {applied_count} jobs.")
            try:
                scroll_container = self.driver.find_element(
                    By.CSS_SELECTOR, ".scaffold-layout__list > div"
                )
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    scroll_container,
                )
                time.sleep(1)
            except (NoSuchElementException, WebDriverException):
                pass
            try:
                if not should_continue():
                    print("Bot stopped by user before next page.")
                    return None
                next_btn = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'button.jobs-search-pagination__button--next[aria-label*="next"]:not([disabled])',
                )
                if next_btn:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", next_btn
                    )
                    time.sleep(1)
                    next_btn.click()
                    time.sleep(3)
                    self.process_job_listings(
                        autofill_path, filters_path, should_continue
                    )
            except (NoSuchElementException, WebDriverException) as e:
                print(f"No more pages or next button not found. Finished. {e}")
        except (FileNotFoundError, json.JSONDecodeError, OSError, WebDriverException, TimeoutException) as e:
            print("Error in process_job_listings:", e)
            return False

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def is_running(self):
        return self.driver is not None
