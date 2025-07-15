import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from browser_control.browser_manager_jobs import *
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
            # Load browser settings
            settings_data, message = ConfigurationManager.load_settings(
                self.settings_path
            )
            if settings_data is None:
                print(f"Failed to load settings: {message}")
                return False

            executable_path = settings_data.get("executable_path", "")
            user_data_dir = str(PROFILE_DIR)
            profile_directory = "Default"

            # Build Chrome options using ChromeOptionsBuilder
            chrome_options = ChromeOptionsBuilder.build_options(
                executable_path, user_data_dir, profile_directory
            )

            # Create WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Execute anti-detection script
            self.driver.execute_script(ChromeOptionsBuilder.get_anti_detection_script())

            return True
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
            WebDriverException,
        ) as e:
            print(f"Failed to start browser: {e}")
            return False

    def go_to_url(self, url):
        if self.driver:
            self.driver.get(url)

    def _load_configuration(self, autofill_path, filters_path=None):
        """Load configuration and filters for job processing."""
        autofill_data, filters, message = ConfigurationManager.load_configuration(
            autofill_path, filters_path
        )

        if autofill_data is None:
            print(f"Configuration loading failed: {message}")
            return None, None

        print(f"DEBUG: {message}")
        if filters:
            print(f"DEBUG: Raw titleSkipWords: {filters.get('titleSkipWords', [])}")

        return autofill_data, filters

    def _get_job_cards(self):
        """Get job cards from the current page."""
        WebDriverWait(self.driver, 20)
        time.sleep(2)

        element_extractor = JobElementExtractor(self.driver)
        job_cards, message = element_extractor.get_job_cards()

        print(f"Found {len(job_cards)} job cards on page")
        return job_cards

    def _filter_jobs(self, job_cards, filters, should_continue):
        """Filter job cards based on configured criteria."""
        job_filter = JobFilter(filters)
        element_extractor = JobElementExtractor(self.driver)

        # Print filter summary
        filter_summary = job_filter.get_filter_summary()
        print(
            f"Filter settings: titleFilterWords={filter_summary['titleFilterWords']}, "
            f"titleSkipWords={filter_summary['titleSkipWords']}, "
            f"badWords={filter_summary['badWords']}"
        )
        print(f"DEBUG: Full titleSkipWords = {job_filter.title_skip_words}")
        print(
            f"DEBUG: 'senior' in titleSkipWords = {'senior' in job_filter.title_skip_words}"
        )

        filtered_jobs = []
        for idx, job_card in enumerate(job_cards):
            if not should_continue():
                print("Bot stopped by user during filtering.")
                return None

            try:
                print(f"\nProcessing job card {idx + 1}/{len(job_cards)}")

                # Check if already applied
                already_applied, apply_message = element_extractor.is_already_applied(
                    job_card
                )
                if already_applied:
                    print(f"  Job {idx + 1}: {apply_message} - SKIPPING")
                    continue

                # Find job title element
                job_title_el, title_message = element_extractor.find_job_title_element(
                    job_card
                )
                if job_title_el is None:
                    print(f"  Job {idx + 1}: {title_message} - SKIPPING")
                    continue

                print(f"  DEBUG: {title_message}")

                # Get job title and details
                raw_title = job_title_el.text.strip()
                aria_label = job_title_el.get_attribute("aria-label") or ""
                job_title = raw_title.lower()

                print(
                    f"  Job {idx + 1}: Raw title = '{raw_title}', Processed title = '{job_title}'"
                )
                print(f"  DEBUG: aria-label = '{aria_label}'")

                # Get subtitle if available
                subtitle, subtitle_message = element_extractor.get_job_subtitle(
                    job_card
                )
                if subtitle:
                    print(f"  Job {idx + 1}: Subtitle = '{subtitle}'")

                # Apply title filters
                should_skip, skip_reason = job_filter.should_skip_by_title(raw_title)
                if should_skip:
                    print(f"  Job {idx + 1}: {skip_reason} - SKIPPING")
                    continue
                else:
                    print(f"  Job {idx + 1}: {skip_reason} - OK")

                print(f"  Job {idx + 1}: PASSED ALL FILTERS - Adding to filtered jobs")
                # Store the original index along with the job card and title element
                filtered_jobs.append((idx, job_card, job_title_el))

            except (
                NoSuchElementException,
                StaleElementReferenceException,
                WebDriverException,
            ) as e:
                print(f"  Job {idx + 1}: Error filtering job: {e} - SKIPPING")

        print(
            f"\nFiltering complete: {len(filtered_jobs)} jobs passed filters out of {len(job_cards)} total jobs"
        )
        return filtered_jobs

    def _apply_to_jobs(self, filtered_jobs, autofill_data, filters, should_continue):
        """Apply to filtered jobs."""
        job_filter = JobFilter(filters)
        element_extractor = JobElementExtractor(self.driver)
        applied_count = 0

        for filter_idx, (original_idx, job_card, job_title_el) in enumerate(
            filtered_jobs
        ):
            if not should_continue():
                print("Bot stopped by user during job application.")
                return None

            try:
                print(
                    f"\nApplying to filtered job {filter_idx + 1}/{len(filtered_jobs)} (original position {original_idx + 1})"
                )

                # Re-find job cards to avoid stale element reference
                current_job_cards, _ = element_extractor.get_job_cards()

                if original_idx >= len(current_job_cards):
                    print(
                        f"  Job {filter_idx + 1}: Job card no longer available at original position {original_idx + 1} - SKIPPING"
                    )
                    continue

                current_job_card = current_job_cards[original_idx]

                # Re-find job title element
                current_job_title_el, title_message = (
                    element_extractor.find_job_title_element(current_job_card)
                )
                if current_job_title_el is None:
                    print(
                        f"  Job {filter_idx + 1}: Could not re-find job title element - SKIPPING"
                    )
                    continue

                time.sleep(0.5)

                print(f"  Clicking on job title to open details...")
                current_job_title_el.click()
                time.sleep(2)

                # Check badWords in job details
                job_details, details_message = element_extractor.get_job_details()
                if job_details is not None:
                    should_skip, skip_reason = job_filter.should_skip_by_description(
                        job_details
                    )
                    if should_skip:
                        print(f"  {skip_reason} - SKIPPING")
                        continue
                    else:
                        print(f"  {skip_reason} - OK")
                else:
                    print(
                        f"  Could not check job details for bad words: {details_message} - Proceeding anyway"
                    )

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

            except (
                NoSuchElementException,
                StaleElementReferenceException,
                WebDriverException,
                TimeoutException,
            ) as e:
                print(f"  Error processing filtered job {filter_idx + 1}: {e}")

        print(f"\nCompleted job applications. Applied to {applied_count} jobs.")
        return applied_count

    def _navigate_to_next_page(self, should_continue):
        """Navigate to the next page of job listings."""
        element_extractor = JobElementExtractor(self.driver)

        # Scroll job list to bottom
        scroll_success, scroll_message = element_extractor.scroll_job_list_to_bottom()
        if scroll_success:
            time.sleep(1)

        # Check if user wants to continue
        if not should_continue():
            print("Bot stopped by user before next page.")
            return False

        # Find and click next button
        next_btn, next_message = element_extractor.scroll_to_next_page_button()
        if next_btn:
            time.sleep(1)
            next_btn.click()
            time.sleep(3)
            return True
        else:
            print(f"No more pages or next button not found. Finished. {next_message}")
            return False

    def process_job_listings(
        self, autofill_path, filters_path=None, should_continue=lambda: True
    ):
        """Main method to process job listings with filtering and application."""
        if not self.driver:
            print("No driver")
            return False

        try:
            # Load configuration and filters
            autofill_data, filters = self._load_configuration(
                autofill_path, filters_path
            )
            if autofill_data is None:
                return False

            while True:
                # Get job cards from current page
                job_cards = self._get_job_cards()
                if not job_cards:
                    print("No job cards found on page")
                    break

                # Filter jobs based on criteria
                filtered_jobs = self._filter_jobs(job_cards, filters, should_continue)
                if filtered_jobs is None:  # User stopped during filtering
                    return None

                # Apply to filtered jobs
                applied_count = self._apply_to_jobs(
                    filtered_jobs, autofill_data, filters, should_continue
                )
                if applied_count is None:  # User stopped during application
                    return None

                # Navigate to next page
                if not self._navigate_to_next_page(should_continue):
                    break

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
            WebDriverException,
            TimeoutException,
        ) as e:
            print("Error in process_job_listings:", e)
            return False

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
