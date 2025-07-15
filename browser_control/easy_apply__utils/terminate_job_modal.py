from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .handle_save_modal import handle_save_application_modal
from .wait_for_elements import wait_for_element, wait_for_elements, smart_delay


def terminate_job_modal(driver, context=None):
    """
    Terminate a job modal by properly closing it and handling any save modals.
    Based on Chrome extension terminateJobModel function.
    """
    if context is None:
        context = driver

    # First, check and handle save modal
    if handle_save_application_modal(driver):
        print("Save modal handled, exiting terminateJobModal")
        return True

    # Look for the dismissed button
    dismiss_button = None
    try:
        dismiss_button = context.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Dismiss"]'
        )
    except NoSuchElementException:
        pass

    if dismiss_button:
        print("Clicking dismiss button in terminateJobModal")
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", dismiss_button
            )
            smart_delay(0.3)
            dismiss_button.click()
            smart_delay(1.0)

            # Check again for save modal after dismissing
            if handle_save_application_modal(driver):
                print("Save modal handled after dismiss")
                return True

            # Look for separate discard button
            discard_buttons = wait_for_elements(
                driver, "button[data-test-dialog-secondary-btn]", timeout=2
            )
            for button in discard_buttons:
                if "discard" in button.text.lower():
                    print("Clicking separate discard button")
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", button
                    )
                    smart_delay(0.3)
                    button.click()
                    smart_delay(0.5)
                    break

        except Exception as e:
            print(f"Error clicking dismiss button: {e}")

    else:
        print("No dismiss button found in terminateJobModal")
        # Try to find available buttons for debugging
        try:
            buttons = context.find_elements(By.TAG_NAME, "button")
            available_buttons = []
            for btn in buttons:
                try:
                    available_buttons.append(
                        {
                            "text": btn.text.strip(),
                            "aria_label": btn.get_attribute("aria-label"),
                        }
                    )
                except:
                    pass
            print(f"Available buttons: {available_buttons}")
        except:
            pass

    return True


def close_all_modals(driver):
    """
    Close all art deco modals on the page.
    """
    try:
        # First handle save modal
        handle_save_application_modal(driver)

        # Then close any remaining modals
        modals = wait_for_elements(driver, ".artdeco-modal", timeout=2)
        for modal in modals:
            try:
                terminate_job_modal(driver, modal)
                smart_delay(0.5)
            except Exception as e:
                print(f"Error closing modal: {e}")

        # Look for "No thanks" buttons
        artdeco_modal = wait_for_element(driver, '[class*="artdeco-modal"]', timeout=2)
        if artdeco_modal:
            buttons = artdeco_modal.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    if "no thanks" in button.text.lower():
                        button.click()
                        smart_delay(0.5)
                        break
                except:
                    continue

    except Exception as e:
        print(f"Error in close_all_modals: {e}")
    """
    Close the "Application sent" modal if it exists.
    """
    try:
        modal = wait_for_element(driver, ".artdeco-modal", timeout=2)
        if (
            modal
            and "application sent" in modal.text.lower()
            and "your application was sent to" in modal.text.lower()
        ):
            dismiss_btn = modal.find_element(By.CSS_SELECTOR, ".artdeco-modal__dismiss")
            if dismiss_btn:
                dismiss_btn.click()
                smart_delay(0.5)
                return True
    except:
        pass
    return False
