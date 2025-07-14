from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .wait_for_elements import wait_for_element, smart_delay


def handle_save_application_modal(driver, max_attempts=3):
    """
    Handle the "Save this application?" modal that appears on LinkedIn.
    Returns True if modal was found and handled, False otherwise.
    """
    attempts = 0

    while attempts < max_attempts:
        try:
            # Look for the save modal with specific selectors
            save_modal = wait_for_element(
                driver, '[data-test-modal=""][role="alertdialog"]', timeout=2
            )

            if not save_modal:
                return False

            # Check if it's actually a save application modal
            title_element = None
            try:
                title_element = save_modal.find_element(
                    By.CSS_SELECTOR, "h2[data-test-dialog-title]"
                )
            except NoSuchElementException:
                pass

            if not title_element or "Save this application?" not in title_element.text:
                return False

            print("Save application modal detected - attempting to close")

            # First, try to find and click the "Discard" button
            discard_button = None
            try:
                discard_button = save_modal.find_element(
                    By.CSS_SELECTOR, "button[data-test-dialog-secondary-btn]"
                )
                if discard_button and "discard" in discard_button.text.lower():
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        discard_button,
                    )
                    smart_delay(0.3)
                    discard_button.click()
                    smart_delay(1.0)

                    # Check if modal is gone
                    if not wait_for_element(
                        driver, '[data-test-modal=""][role="alertdialog"]', timeout=2
                    ):
                        print("Save modal successfully closed with Discard button")
                        return True
                    else:
                        print("Save modal still exists after Discard click")

            except NoSuchElementException:
                pass

            # Fallback: try to find and click the "Dismiss" button
            dismiss_button = None
            try:
                dismiss_button = save_modal.find_element(
                    By.CSS_SELECTOR, 'button[aria-label="Dismiss"]'
                )
                if dismiss_button:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        dismiss_button,
                    )
                    smart_delay(0.3)
                    dismiss_button.click()
                    smart_delay(1.0)

                    # Check if modal is gone
                    if not wait_for_element(
                        driver, '[data-test-modal=""][role="alertdialog"]', timeout=2
                    ):
                        print("Save modal successfully closed with Dismiss button")
                        return True
                    else:
                        print("Save modal still exists after Dismiss click")

            except NoSuchElementException:
                pass

            print(f"Save modal handling failed, attempt {attempts + 1}/{max_attempts}")
            attempts += 1
            smart_delay(0.5)

        except Exception as e:
            print(f"Error handling save modal: {e}")
            attempts += 1
            smart_delay(0.5)

    return False


def check_for_save_modal(driver):
    """
    Quick check if save modal is present without trying to handle it.
    """
    try:
        save_modal = wait_for_element(
            driver, '[data-test-modal=""][role="alertdialog"]', timeout=1
        )

        if save_modal:
            title_element = None
            try:
                title_element = save_modal.find_element(
                    By.CSS_SELECTOR, "h2[data-test-dialog-title]"
                )
                if title_element and "Save this application?" in title_element.text:
                    return True
            except NoSuchElementException:
                pass

        return False
    except:
        return False
