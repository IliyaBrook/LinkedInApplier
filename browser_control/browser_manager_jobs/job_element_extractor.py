from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class JobElementExtractor:
    def __init__(self, driver):
        """Initialize with a WebDriver instance."""
        self.driver = driver

    @staticmethod
    def find_job_title_element(job_card):
        """Find a job title element using fallback selectors."""
        try:
            job_title_el = job_card.find_element(
                By.CSS_SELECTOR,
                ".artdeco-entity-lockup__title .job-card-container__link",
            )
            return job_title_el, "Found job title element with first selector"
        except NoSuchElementException:
            try:
                job_title_el = job_card.find_element(
                    By.CSS_SELECTOR, ".job-card-container__link"
                )
                return job_title_el, "Found job title element with second selector"
            except NoSuchElementException:
                return None, "No job title link found"

    @staticmethod
    def is_already_applied(job_card):
        """Check if a job has already been applied to."""
        try:
            applied_footer = job_card.find_element(
                By.CSS_SELECTOR, ".job-card-container__footer-job-state"
            )
            footer_text = applied_footer.text.strip().lower()
            if "applied" in footer_text:
                return True, f"Already applied (footer: '{footer_text}')"
            return False, "Not applied yet"
        except NoSuchElementException:
            return False, "No application status found"

    def get_job_details(self):
        """Get job details from the current job page."""
        try:
            job_details_element = self.driver.find_element(
                By.CSS_SELECTOR, '[class*="jobs-box__html-content"]'
            )
            return (
                job_details_element.text.lower(),
                "Job details retrieved successfully",
            )
        except NoSuchElementException:
            return None, "Could not find job details element"

    def get_job_cards(self):
        """Get all job cards from the current page."""
        try:
            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".scaffold-layout__list-item"
            )
            return job_cards, f"Found {len(job_cards)} job cards"
        except Exception as e:
            return [], f"Error finding job cards: {e}"

    @staticmethod
    def get_job_subtitle(job_card):
        """Get job subtitle/company info from the job card."""
        try:
            subtitle = (
                job_card.find_element(
                    By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle"
                )
                .text.strip()
                .lower()
            )
            return subtitle, "Subtitle found"
        except NoSuchElementException:
            return None, "No subtitle found"

    def scroll_to_next_page_button(self):
        """Scroll to and find the next page button."""
        try:
            next_btn = self.driver.find_element(
                By.CSS_SELECTOR,
                'button.jobs-search-pagination__button--next[aria-label*="next"]:not([disabled])',
            )
            if next_btn:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", next_btn
                )
                return next_btn, "Next button found and scrolled to"
            return None, "Next button not found"
        except NoSuchElementException:
            return None, "Next button not found"

    def scroll_job_list_to_bottom(self):
        """Scroll the job list container to the bottom."""
        try:
            scroll_container = self.driver.find_element(
                By.CSS_SELECTOR, ".scaffold-layout__list > div"
            )
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                scroll_container,
            )
            return True, "Scrolled job list to bottom"
        except NoSuchElementException:
            return False, "Could not find scroll container"
