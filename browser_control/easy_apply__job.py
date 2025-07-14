import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from browser_control.browser_utils import (
    scroll_to_and_click,
    scroll_to_element,
    wait_for_elements,
    wait_for_element,
    wait_for_clickable_element,
    smart_delay,
    handle_save_application_modal,
    check_for_save_modal,
    terminate_job_modal,
    close_all_modals,
    close_application_sent_modal,
)


def apply_to_job(driver, autofill_data):
    """
    Apply to job using Easy Apply with improved modal handling and speed.
    Based on Chrome extension logic.
    """
    try:
        # First, handle any existing save modals
        if handle_save_application_modal(driver):
            print("Save modal handled before starting application")
            return True

        # Check if already applied (like in Chrome extension)
        already_applied_element = wait_for_element(
            driver, ".artdeco-inline-feedback__message", timeout=2
        )
        if already_applied_element:
            text_content = already_applied_element.text
            if check_if_already_applied(text_content):
                print(f"Already applied to this job: {text_content}")
                return True

        # Find Easy Apply button using multiple selectors (updated based on real HTML structure)
        easy_apply_btn = None

        # First, try to find the detail section
        detail_section = None
        try:
            detail_section = driver.find_element(
                By.CSS_SELECTOR, ".scaffold-layout__detail"
            )
            print("Found scaffold-layout__detail section")
        except:
            print("scaffold-layout__detail section not found, searching in full page")
            detail_section = driver

        # Try different selectors for Easy Apply button - updated based on real HTML structure
        selectors = [
            "#jobs-apply-button-id",  # Direct ID selector (most reliable)
            "button[aria-label*='Easy Apply']",  # Contains "Easy Apply" (not exact match)
            ".jobs-apply-button",  # Class selector from example
            "button[class*='jobs-apply-button']",  # Any button with jobs-apply-button in class
            ".jobs-apply-button--top-card",
            "button[data-control-name='jobdetails_topcard_inapply']",
            "//button[contains(@aria-label, 'Easy Apply')]",  # XPath with contains
            "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]",
        ]

        print(
            f"Looking for Easy Apply button with {len(selectors)} different selectors in detail section..."
        )

        for i, selector in enumerate(selectors):
            try:
                if selector.startswith("//"):
                    if detail_section == driver:
                        easy_apply_btn = wait_for_clickable_element(
                            driver, selector, timeout=2, by=By.XPATH
                        )
                    else:
                        # For XPath in a specific context, need to adjust
                        easy_apply_btn = detail_section.find_elements(
                            By.XPATH,
                            ".//button[contains(@aria-label, 'Easy Apply') or contains(., 'Easy Apply')]",
                        )
                        easy_apply_btn = easy_apply_btn[0] if easy_apply_btn else None
                else:
                    if detail_section == driver:
                        easy_apply_btn = wait_for_clickable_element(
                            driver, selector, timeout=2
                        )
                    else:
                        try:
                            easy_apply_btn = detail_section.find_element(
                                By.CSS_SELECTOR, selector
                            )
                        except:
                            easy_apply_btn = None

                if easy_apply_btn:
                    # Verify this is actually "Easy Apply" and not regular "Apply"
                    aria_label = easy_apply_btn.get_attribute("aria-label") or ""
                    button_text = easy_apply_btn.text.strip()

                    print(
                        f"Found button with selector #{i+1}: aria-label='{aria_label}', text='{button_text}'"
                    )

                    # Check if it's Easy Apply (not regular Apply)
                    if (
                        "easy apply" in aria_label.lower()
                        or "easy apply" in button_text.lower()
                    ):
                        print(
                            f"✅ Confirmed Easy Apply button with selector #{i+1}: {selector}"
                        )
                        break
                    elif (
                        "apply" in aria_label.lower()
                        and "easy apply" not in aria_label.lower()
                    ):
                        print(
                            f"❌ This is regular Apply button (not Easy Apply) - skipping"
                        )
                        # TODO: Add logic for regular Apply buttons (external company website)
                        easy_apply_btn = None
                        continue
                    else:
                        print(f"Found button with selector #{i+1}: {selector}")
                        break
                else:
                    print(f"Selector #{i+1} failed: {selector}")
            except Exception as e:
                print(f"Error with selector #{i+1} ({selector}): {e}")

        if not easy_apply_btn:
            print("Easy Apply button not found on job page")

            # Debug: show what buttons are available in detail section
            try:
                search_context = detail_section if detail_section != driver else driver
                all_buttons = search_context.find_elements(By.TAG_NAME, "button")
                print(f"Found {len(all_buttons)} buttons in detail section:")
                for btn in all_buttons[:10]:  # Show first 10 buttons
                    try:
                        aria_label = btn.get_attribute("aria-label") or "No aria-label"
                        btn_class = btn.get_attribute("class") or "No class"
                        btn_text = btn.text.strip() or "No text"
                        btn_id = btn.get_attribute("id") or "No id"
                        print(
                            f"  Button: id='{btn_id}', aria-label='{aria_label}', class='{btn_class}', text='{btn_text}'"
                        )
                    except:
                        pass
            except Exception as e:
                print(f"Could not debug buttons: {e}")

            return False

        print(f"Clicking Easy Apply button...")
        easy_apply_btn.click()
        smart_delay(2.0)  # Give more time for modal to appear

        # Debug what appears after clicking
        print("Checking what appeared after clicking Easy Apply...")
        try:
            # Check for any new elements that might be modals
            potential_modals = driver.find_elements(
                By.CSS_SELECTOR,
                "[class*='modal'], [class*='dialog'], [role='dialog'], [data-test-modal], .artdeco-modal",
            )
            print(
                f"Found {len(potential_modals)} potential modal elements immediately after click:"
            )
            for i, modal in enumerate(potential_modals[:3]):
                try:
                    classes = modal.get_attribute("class") or "No class"
                    role = modal.get_attribute("role") or "No role"
                    data_test = modal.get_attribute("data-test-modal") or "No data-test"
                    is_displayed = modal.is_displayed()
                    text_snippet = modal.text[:100] if modal.text else "No text"
                    print(
                        f"  Potential modal {i+1}: class='{classes}', role='{role}', data-test='{data_test}', displayed={is_displayed}, text='{text_snippet}...'"
                    )
                except:
                    pass
        except Exception as e:
            print(f"Could not debug potential modals: {e}")

        # Main application loop with timeout
        max_iterations = 10
        iteration = 0

        print(f"Starting main application loop...")

        while iteration < max_iterations:
            # Check for save modal at start of each iteration
            if handle_save_application_modal(driver):
                print("Save modal handled during application process")
                return True

            # Try different selectors for modal windows
            modal_selectors = [
                ".artdeco-modal",
                "[data-test-modal]",
                ".jobs-easy-apply-modal",
                ".ember-application .ember-view .artdeco-modal",
                "[role='dialog']",
                ".artdeco-modal--layer-default",
            ]

            apply_modal = None
            used_selector = None

            for selector in modal_selectors:
                apply_modal = wait_for_element(driver, selector, timeout=3)
                if apply_modal:
                    used_selector = selector
                    print(f"Modal found with selector: {selector}")
                    break

            if not apply_modal:
                print(
                    f"No modal found with any selector after {iteration + 1} attempts"
                )

                # Debug: show what's on the page
                try:
                    print("Debugging - looking for any modal-like elements:")
                    all_modals = driver.find_elements(
                        By.CSS_SELECTOR,
                        "[class*='modal'], [class*='dialog'], [role='dialog']",
                    )
                    print(f"Found {len(all_modals)} modal-like elements:")
                    for i, modal in enumerate(all_modals[:5]):  # Show first 5
                        try:
                            classes = modal.get_attribute("class") or "No class"
                            role = modal.get_attribute("role") or "No role"
                            text_snippet = modal.text[:100] if modal.text else "No text"
                            print(
                                f"  Modal {i+1}: class='{classes}', role='{role}', text='{text_snippet}...'"
                            )
                        except:
                            pass
                except Exception as e:
                    print(f"Could not debug modals: {e}")

                # Check if application was already submitted
                success_messages = wait_for_elements(
                    driver, '[data-test-modal=""]', timeout=2
                )
                if success_messages:
                    for msg in success_messages:
                        if any(
                            keyword in msg.text.lower()
                            for keyword in ["sent", "submitted", "application"]
                        ):
                            print(f"Application success message found: {msg.text}")
                            close_all_modals(driver)
                            return True

                # If still no modal after reasonable time, break
                if iteration >= 3:
                    print(
                        "No application modal found after multiple attempts - this might be an error"
                    )
                    return False

                smart_delay(2.0)
                iteration += 1
                continue

            print(f"Modal found! Processing application form...")

            # Find form within modal
            form = None
            try:
                form = apply_modal.find_element(By.CSS_SELECTOR, "form")
                print(f"Form found in modal")
            except NoSuchElementException:
                print(f"No form found in modal")
                pass

            if not form:
                print("No form found in modal, checking for completion messages...")

                # Check if application is already complete
                modal_text = apply_modal.text.lower()
                if any(
                    keyword in modal_text
                    for keyword in ["sent", "submitted", "complete", "thank you"]
                ):
                    print(f"Application appears to be complete based on modal text")
                    close_all_modals(driver)
                    return True

                # If no form and no completion message, continue to next iteration
                iteration += 1
                continue

            # Process form fields
            form_updated = process_form_fields(driver, form, autofill_data)

            if form_updated:
                # Save autofill data if it was updated
                with open("DB/form_autofill.json", "w", encoding="utf-8") as f:
                    json.dump(autofill_data, f, ensure_ascii=False, indent=2)

            # Look for next action buttons
            next_action = find_next_action_button(driver, apply_modal)

            if next_action["type"] == "none":
                print(f"❌ No action button found in iteration {iteration + 1}")

                # Try scrolling and looking again before giving up
                if iteration < 2:  # Only retry for first 2 iterations
                    print("Retrying button search after scrolling...")
                    try:
                        # Try scrolling to different parts of the modal
                        driver.execute_script(
                            "arguments[0].scrollTop = 0;", apply_modal
                        )
                        smart_delay(1.0)

                        driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight / 2;",
                            apply_modal,
                        )
                        smart_delay(1.0)

                        driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight;",
                            apply_modal,
                        )
                        smart_delay(1.0)

                        # Try finding buttons again
                        next_action = find_next_action_button(driver, apply_modal)

                        if next_action["type"] != "none":
                            print(f"✅ Found button after retry: {next_action['type']}")
                        else:
                            print("Still no button found after retry")
                    except Exception as e:
                        print(f"Error during retry: {e}")

                # If still no button found, check if application might be complete
                if next_action["type"] == "none":
                    try:
                        modal_text = apply_modal.text.lower()
                        completion_indicators = [
                            "application sent",
                            "application submitted",
                            "thank you",
                            "your application has been sent",
                            "successfully submitted",
                            "application complete",
                        ]

                        if any(
                            indicator in modal_text
                            for indicator in completion_indicators
                        ):
                            print(
                                "✅ Application appears to be complete based on modal text"
                            )
                            close_all_modals(driver)
                            return True

                        print("No completion indicators found in modal text")
                        print(f"Modal text snippet: {modal_text[:200]}...")

                    except Exception as e:
                        print(f"Error checking completion: {e}")

                    print("Terminating application process - no valid buttons found")
                    terminate_job_modal(driver)
                    break

            if next_action["type"] == "submit":
                print("Found submit button, attempting to submit application")

                # Get the submit button
                submit_button = next_action["element"]

                # First, scroll to the bottom of the modal to ensure all elements are visible
                try:
                    driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;",
                        apply_modal,
                    )
                    smart_delay(1.0)
                    print("Scrolled to bottom of modal before submit")
                except:
                    pass

                # Uncheck follow company checkbox if present
                uncheck_follow_company_checkbox(driver)

                # Scroll to submit button and submit application
                print("Scrolling to and clicking Submit button...")
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        submit_button,
                    )
                    smart_delay(1.0)

                    # Make sure button is still clickable
                    if not submit_button.is_enabled():
                        print("⚠️ Submit button is not enabled - waiting...")
                        smart_delay(2.0)

                    # Click submit
                    submit_button.click()
                    print("✅ Submit button clicked successfully")
                    smart_delay(3.0)  # Give more time for submission to process

                    # Handle any save modal after submit
                    if handle_save_application_modal(driver):
                        print("Save modal handled after submit")
                        return True

                    # Check for success message
                    try:
                        success_indicators = [
                            "application sent",
                            "application submitted",
                            "thank you",
                            "your application has been sent",
                            "successfully submitted",
                        ]

                        page_text = driver.page_source.lower()
                        if any(
                            indicator in page_text for indicator in success_indicators
                        ):
                            print(
                                "✅ Application appears to have been submitted successfully"
                            )
                            close_all_modals(driver)
                            return True
                    except:
                        pass

                    # Close any remaining modals
                    close_all_modals(driver)
                    return True

                except Exception as e:
                    print(f"Error clicking submit button: {e}")
                    close_all_modals(driver)
                    return False

            elif next_action["type"] == "next":
                print("Found next/review button, proceeding to next step")

                next_button = next_action["element"]

                # Debug button information
                try:
                    button_text = next_button.text.strip()
                    button_aria = (
                        next_button.get_attribute("aria-label") or "No aria-label"
                    )
                    button_class = next_button.get_attribute("class") or "No class"
                    button_data_attrs = []
                    for attr in [
                        "data-easy-apply-next-button",
                        "data-live-test-easy-apply-next-button",
                        "data-easy-apply-review-button",
                    ]:
                        if next_button.get_attribute(attr):
                            button_data_attrs.append(attr)
                    print(
                        f"Button details: text='{button_text}', aria-label='{button_aria}', data-attrs={button_data_attrs}"
                    )
                except:
                    pass

                try:
                    # Scroll to the button location first
                    print("Scrolling to Next/Review button...")
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        next_button,
                    )
                    smart_delay(1.0)  # Give more time for scroll

                    # Check if button is still enabled and visible
                    if not next_button.is_enabled():
                        print("⚠️ Next/Review button is not enabled, waiting...")
                        smart_delay(2.0)

                    if not next_button.is_displayed():
                        print("⚠️ Next/Review button is not visible after scroll")

                    # Try clicking the button
                    print("Attempting to click Next/Review button...")
                    next_button.click()
                    print("✅ Next/Review button clicked successfully")
                    smart_delay(2.0)  # Give more time for page transition

                    # Handle save modal after next
                    if handle_save_application_modal(driver):
                        print("Save modal handled after next")
                        return True

                    # Check for discard button (indicates we should terminate)
                    discard_buttons = wait_for_elements(
                        driver, "button[data-test-dialog-secondary-btn]", timeout=2
                    )
                    for button in discard_buttons:
                        if "discard" in button.text.lower():
                            print("Discard button found, terminating application")
                            terminate_job_modal(driver)
                            return False

                    # Verify that we moved to next step by checking if modal content changed
                    try:
                        new_modal = wait_for_element(
                            driver, ".artdeco-modal", timeout=3
                        )
                        if new_modal:
                            print("✅ Successfully moved to next step")
                        else:
                            print(
                                "⚠️ Modal disappeared after clicking Next - this might be normal"
                            )
                    except:
                        pass

                except Exception as e:
                    print(f"❌ Error clicking next button: {e}")

                    # Debug: show what buttons are available now
                    try:
                        current_modal = wait_for_element(
                            driver, ".artdeco-modal", timeout=2
                        )
                        if current_modal:
                            all_buttons = current_modal.find_elements(
                                By.TAG_NAME, "button"
                            )
                            print(
                                f"Available buttons after error ({len(all_buttons)}):"
                            )
                            for i, btn in enumerate(all_buttons[:5]):
                                try:
                                    btn_text = btn.text.strip() or "No text"
                                    btn_aria = (
                                        btn.get_attribute("aria-label")
                                        or "No aria-label"
                                    )
                                    btn_displayed = btn.is_displayed()
                                    print(
                                        f"  Button {i+1}: text='{btn_text}', aria='{btn_aria}', displayed={btn_displayed}"
                                    )
                                except:
                                    pass
                    except:
                        pass

                    terminate_job_modal(driver)
                    return False

            elif next_action["type"] == "continue":
                print("Found continue applying button")

                continue_button = next_action["element"]

                try:
                    print("Scrolling to and clicking Continue button...")
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        continue_button,
                    )
                    smart_delay(0.5)

                    continue_button.click()
                    print("✅ Continue button clicked successfully")
                    smart_delay(1.0)

                except Exception as e:
                    print(f"Error clicking continue button: {e}")
                    terminate_job_modal(driver)
                    return False

            # If we reach here with next_action["type"] == "none", it was already handled above
            # Continue to next iteration
            iteration += 1

        # Final cleanup
        close_all_modals(driver)
        return True

    except Exception as e:
        print(f"Error in apply_to_job: {e}")
        try:
            close_all_modals(driver)
        except:
            pass
        return False


def process_form_fields(driver, form, autofill_data):
    """
    Process all form fields (inputs, radio buttons, dropdowns) in the given form.
    """
    updated = False

    # Process input fields
    if process_input_fields(driver, form, autofill_data):
        updated = True

    # Process radio buttons
    if process_radio_buttons(driver, form, autofill_data):
        updated = True

    # Process dropdowns
    if process_dropdowns(driver, form, autofill_data):
        updated = True

    return updated


def process_input_fields(driver, form, autofill_data):
    """
    Process input and textarea fields in the form.
    """
    updated = False
    inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea")

    for field in inputs:
        try:
            tag = field.tag_name
            type_ = field.get_attribute("type")
            name = get_field_name(field, form)
            value = field.get_attribute("value")

            # Handle checkboxes
            if tag == "input" and type_ == "checkbox":
                if not field.is_selected():
                    try:
                        field.click()
                        smart_delay(0.1)
                    except:
                        pass
                continue

            # Handle text inputs
            if (
                tag == "input"
                and type_ in ("text", "email", "tel")
                or tag == "textarea"
            ):
                db_section = "textInput"
                autofill_section = autofill_data.get(db_section, {})
                autofill_val = autofill_section.get(name, None)

                if autofill_val and value != autofill_val:
                    try:
                        field.clear()
                        field.send_keys(autofill_val)
                        smart_delay(0.1)
                    except:
                        pass
                elif not autofill_val and name:
                    if db_section not in autofill_data:
                        autofill_data[db_section] = {}
                    if name not in autofill_data[db_section]:
                        autofill_data[db_section][name] = value or ""
                        updated = True

        except Exception as e:
            print(f"Error processing input field: {e}")

    return updated


def process_radio_buttons(driver, form, autofill_data):
    """
    Process radio button fieldsets in the form.
    """
    updated = False
    radio_fieldsets = form.find_elements(
        By.CSS_SELECTOR,
        'fieldset[data-test-form-builder-radio-button-form-component="true"]',
    )

    for fieldset in radio_fieldsets:
        try:
            legend = fieldset.find_element(By.TAG_NAME, "legend")
            label_el = None
            try:
                label_el = legend.find_element(
                    By.CSS_SELECTOR, 'span[aria-hidden="true"]'
                )
            except:
                pass

            label = label_el.text.strip() if label_el else legend.text.strip()

            options = []
            radios = fieldset.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            selected_value = None

            for radio in radios:
                radio_label = get_radio_label(radio, fieldset)
                options.append(
                    {
                        "value": radio.get_attribute("value"),
                        "text": radio_label,
                        "selected": radio.is_selected(),
                    }
                )
                if radio.is_selected():
                    selected_value = radio.get_attribute("value")

            # Update autofill data
            if "radioButtons" not in autofill_data:
                autofill_data["radioButtons"] = []

            found = next(
                (
                    rb
                    for rb in autofill_data["radioButtons"]
                    if rb["placeholderIncludes"].strip().lower()
                    == label.strip().lower()
                ),
                None,
            )

            if found:
                same_options = found["options"] == options
                same_default = found.get("defaultValue", None) == selected_value
                if not (same_options and same_default):
                    found["options"] = options
                    if selected_value:
                        found["defaultValue"] = selected_value
                    found["count"] += 1
                    updated = True
                else:
                    found["count"] += 1
            else:
                autofill_data["radioButtons"].append(
                    {
                        "placeholderIncludes": label,
                        "defaultValue": selected_value
                        or (options[0]["value"] if options else ""),
                        "count": 1,
                        "createdAt": int(time.time() * 1000),
                        "options": options,
                    }
                )
                updated = True

        except Exception as e:
            print(f"Error processing radio button fieldset: {e}")

    return updated


def process_dropdowns(driver, form, autofill_data):
    """
    Process dropdown select elements in the form.
    """
    updated = False
    selects = form.find_elements(By.TAG_NAME, "select")

    for select in selects:
        try:
            # Get label
            label = get_dropdown_label(select)

            # Get options
            options = []
            for option in select.find_elements(By.TAG_NAME, "option"):
                options.append(
                    {
                        "value": option.get_attribute("value"),
                        "text": option.text.strip(),
                        "selected": option.is_selected(),
                    }
                )

            selected_value = next(
                (o["value"] for o in options if o["selected"]),
                options[0]["value"] if options else "",
            )

            # Update autofill data
            if "dropdowns" not in autofill_data:
                autofill_data["dropdowns"] = []

            found = next(
                (
                    d
                    for d in autofill_data["dropdowns"]
                    if d["placeholderIncludes"].strip().lower() == label.strip().lower()
                ),
                None,
            )

            if found:
                same_options = found["options"] == options
                same_default = found.get("defaultValue", None) == selected_value
                if not (same_options and same_default):
                    found["options"] = options
                    found["defaultValue"] = selected_value
                    found["count"] += 1
                    updated = True
                else:
                    found["count"] += 1
            else:
                autofill_data["dropdowns"].append(
                    {
                        "placeholderIncludes": label,
                        "count": 1,
                        "options": options,
                        "defaultValue": selected_value,
                    }
                )
                updated = True

        except Exception as e:
            print(f"Error processing dropdown: {e}")

    return updated


def get_field_name(field, form):
    """
    Get field name from various attributes.
    """
    name = (
        field.get_attribute("name")
        or field.get_attribute("aria-label")
        or field.get_attribute("placeholder")
    )

    if not name:
        field_id = field.get_attribute("id")
        if field_id:
            try:
                label_el = form.find_element(
                    By.CSS_SELECTOR, f'label[for="{field_id}"]'
                )
                span = None
                try:
                    span = label_el.find_element(
                        By.CSS_SELECTOR, 'span[aria-hidden="true"]'
                    )
                except:
                    pass
                name = span.text.strip() if span else label_el.text.strip()
            except:
                pass

    return name


def get_radio_label(radio, fieldset):
    """
    Get label text for a radio button.
    """
    radio_label = ""
    try:
        radio_label_el = fieldset.find_element(
            By.CSS_SELECTOR, f'label[for="{radio.get_attribute("id")}"]'
        )
        radio_label = radio_label_el.text.strip()
    except:
        pass

    if not radio_label:
        parent = radio.find_element(By.XPATH, "..")
        spans = parent.find_elements(By.TAG_NAME, "span")
        for s in spans:
            t = s.text.strip()
            if t:
                radio_label = t
                break

    return radio_label


def get_dropdown_label(select):
    """
    Get label text for a dropdown select element.
    """
    try:
        parent = select.find_element(
            By.XPATH, "ancestor::div[contains(@class, 'fb-dash-form-element')]"
        )
        label_el = parent.find_element(By.TAG_NAME, "label")

        aria_hidden = None
        try:
            aria_hidden = label_el.find_element(
                By.CSS_SELECTOR, 'span[aria-hidden="true"]'
            )
        except:
            pass

        label = aria_hidden.text.strip() if aria_hidden else label_el.text.strip()
        return label
    except:
        return f"Dropdown {int(time.time())}"


def find_next_action_button(driver, modal):
    """
    Find the next action button (submit, next, review, continue).
    Uses scrolling to ensure buttons are visible.
    Returns dict with type and element.
    """
    print("Looking for next action button...")

    # First scroll to bottom of modal to ensure all buttons are visible
    try:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;", modal
        )
        smart_delay(0.5)
        print("Scrolled to bottom of modal")
    except:
        pass

    # Check for continue applying button
    continue_btn = None
    try:
        continue_btn = modal.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Continue applying"]'
        )
        if continue_btn and continue_btn.is_displayed():
            print("Found 'Continue applying' button")
            return {"type": "continue", "element": continue_btn}
    except:
        pass

    # Check for submit button with multiple selectors
    submit_selectors = [
        'button[aria-label="Submit application"]',
        "button[data-live-test-easy-apply-submit-button]",
        'button[class*="artdeco-button--primary"]:contains("Submit")',
        'button:contains("Submit application")',
        '.artdeco-button--primary[type="button"]:contains("Submit")',
    ]

    submit_btn = None
    for selector in submit_selectors:
        try:
            if ":contains(" in selector:
                # Use XPath for text-based selectors
                xpath_selector = f"//button[contains(text(), 'Submit')]"
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed() and (
                        "submit" in elem.text.lower()
                        or "submit" in elem.get_attribute("aria-label", "").lower()
                    ):
                        submit_btn = elem
                        break
            else:
                submit_btn = modal.find_element(By.CSS_SELECTOR, selector)
                if submit_btn and submit_btn.is_displayed():
                    break
        except:
            continue

    if submit_btn:
        print(
            f"Found Submit application button: {submit_btn.get_attribute('aria-label') or submit_btn.text}"
        )

        # Scroll to submit button to ensure it's visible
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                submit_btn,
            )
            smart_delay(0.5)
            print("Scrolled to Submit button")
        except:
            pass

        return {"type": "submit", "element": submit_btn}

    # Check for review button
    review_selectors = [
        'button[aria-label="Review your application"]',
        'button[aria-label*="Review"]',
        "button[data-easy-apply-review-button]",
        "button[data-live-test-easy-apply-review-button]",
        'button:contains("Review")',
        '//button[contains(text(), "Review")]',
        '//button[contains(@aria-label, "Review")]',
    ]

    review_btn = None
    for selector in review_selectors:
        try:
            if selector.startswith("//"):
                elements = modal.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed():
                        review_btn = elem
                        break
            elif ":contains(" in selector:
                xpath_selector = f"//button[contains(text(), 'Review')]"
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed():
                        review_btn = elem
                        break
            else:
                review_btn = modal.find_element(By.CSS_SELECTOR, selector)
                if review_btn and review_btn.is_displayed():
                    break
        except:
            continue

    if review_btn:
        print(
            f"Found Review button: {review_btn.get_attribute('aria-label') or review_btn.text}"
        )
        # Scroll to review button
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                review_btn,
            )
            smart_delay(0.5)
            print("Scrolled to Review button")
        except:
            pass
        return {"type": "next", "element": review_btn}

    # Check for next button (generic) - improved with more selectors
    next_selectors = [
        'button[aria-label="Continue to next step"]',  # From user's example
        "button[data-easy-apply-next-button]",  # From user's example
        "button[data-live-test-easy-apply-next-button]",  # From user's example
        'button[aria-label*="Next"]',
        'button[aria-label*="Continue"]',
        'button:contains("Next")',
        '.artdeco-button--primary:contains("Next")',
        '//button[contains(text(), "Next")]',
        '//button[contains(@aria-label, "Next")]',
        '//button[contains(@aria-label, "Continue")]',
        "//button[@data-easy-apply-next-button]",
        "//button[@data-live-test-easy-apply-next-button]",
    ]

    next_btn = None
    for selector in next_selectors:
        try:
            if selector.startswith("//"):
                elements = modal.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed():
                        next_btn = elem
                        break
            elif ":contains(" in selector:
                xpath_selector = f"//button[contains(text(), 'Next')]"
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed():
                        next_btn = elem
                        break
            else:
                next_btn = modal.find_element(By.CSS_SELECTOR, selector)
                if next_btn and next_btn.is_displayed():
                    break
        except:
            continue

    if next_btn:
        print(
            f"Found Next button: {next_btn.get_attribute('aria-label') or next_btn.text}"
        )
        # Scroll to next button
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                next_btn,
            )
            smart_delay(0.5)
            print("Scrolled to Next button")
        except:
            pass
        return {"type": "next", "element": next_btn}

    # Debug: show all buttons in modal if none found
    try:
        all_buttons = modal.find_elements(By.TAG_NAME, "button")
        print(
            f"No action button found. Available buttons in modal ({len(all_buttons)}):"
        )
        for i, btn in enumerate(all_buttons[:10]):
            try:
                aria_label = btn.get_attribute("aria-label") or "No aria-label"
                btn_text = btn.text.strip() or "No text"
                btn_class = btn.get_attribute("class") or "No class"
                is_displayed = btn.is_displayed()
                print(
                    f"  Button {i+1}: aria-label='{aria_label}', text='{btn_text}', displayed={is_displayed}, class='{btn_class}'"
                )
            except:
                pass
    except:
        pass

    return {"type": "none", "element": None}


def uncheck_follow_company_checkbox(driver):
    """
    Uncheck the follow company checkbox if it exists and is checked.
    Uses scrolling to ensure the checkbox is visible and handles visually-hidden inputs.
    """
    try:
        print("Looking for follow company checkbox...")

        # First, try to find the footer section containing the checkbox
        footer_section = None
        try:
            footer_section = driver.find_element(
                By.CSS_SELECTOR, ".job-details-easy-apply-footer__section"
            )
            print("Found follow company footer section")
        except:
            print("Follow company footer section not found, searching in full page")

        # Try multiple selectors for the checkbox
        checkbox_selectors = [
            "#follow-company-checkbox",
            "input[id='follow-company-checkbox']",
            "input[type='checkbox'][id*='follow']",
            ".ember-checkbox[id*='follow']",
        ]

        follow_checkbox = None
        used_selector = None

        search_context = footer_section if footer_section else driver

        for selector in checkbox_selectors:
            try:
                follow_checkbox = search_context.find_element(By.CSS_SELECTOR, selector)
                if follow_checkbox:
                    used_selector = selector
                    print(f"Found follow company checkbox with selector: {selector}")
                    break
            except:
                continue

        if not follow_checkbox:
            print("Follow company checkbox not found - skipping")
            return

        # Get checkbox info for debugging
        try:
            checkbox_classes = follow_checkbox.get_attribute("class") or "No class"
            checkbox_id = follow_checkbox.get_attribute("id") or "No id"
            is_hidden = (
                "visually-hidden" in checkbox_classes or "hidden" in checkbox_classes
            )
            print(
                f"Checkbox details: id='{checkbox_id}', class='{checkbox_classes}', visually_hidden={is_hidden}"
            )
        except:
            is_hidden = False

        # Check if checkbox is checked
        is_checked = follow_checkbox.is_selected()
        print(f"Follow company checkbox is {'checked' if is_checked else 'unchecked'}")

        if is_checked:
            print("Unchecking follow company checkbox...")

            # Scroll to the footer section or checkbox first
            scroll_target = footer_section if footer_section else follow_checkbox
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                scroll_target,
            )
            smart_delay(0.8)
            print("Scrolled to follow company section")

            # If checkbox is visually hidden, click the label instead
            if is_hidden or not follow_checkbox.is_displayed():
                print("Checkbox is visually hidden, looking for label to click...")
                try:
                    # Find the label element
                    label_selectors = [
                        f"label[for='{follow_checkbox.get_attribute('id')}']",
                        "label[for='follow-company-checkbox']",
                        ".job-details-easy-apply-footer__section label",
                    ]

                    label_element = None
                    for label_selector in label_selectors:
                        try:
                            label_element = search_context.find_element(
                                By.CSS_SELECTOR, label_selector
                            )
                            if label_element:
                                print(f"Found label with selector: {label_selector}")
                                break
                        except:
                            continue

                    if label_element:
                        print("Clicking label to uncheck hidden checkbox...")
                        label_element.click()
                        smart_delay(0.5)
                    else:
                        print("Label not found, trying to click checkbox directly...")
                        driver.execute_script("arguments[0].click();", follow_checkbox)
                        smart_delay(0.5)

                except Exception as e:
                    print(f"Error clicking label: {e}, trying direct click...")
                    driver.execute_script("arguments[0].click();", follow_checkbox)
                    smart_delay(0.5)
            else:
                # Checkbox is visible, click it directly
                print("Clicking visible checkbox...")
                follow_checkbox.click()
                smart_delay(0.5)

            # Verify it was unchecked
            smart_delay(0.3)
            try:
                is_still_checked = follow_checkbox.is_selected()
                if not is_still_checked:
                    print("✅ Successfully unchecked follow company checkbox")
                else:
                    print("⚠️ Checkbox might still be checked, trying one more time...")
                    # Try one more time with different method
                    if is_hidden:
                        driver.execute_script(
                            "arguments[0].checked = false;", follow_checkbox
                        )
                    else:
                        follow_checkbox.click()
                    smart_delay(0.3)
                    if not follow_checkbox.is_selected():
                        print("✅ Successfully unchecked on second attempt")
                    else:
                        print("⚠️ Could not uncheck checkbox - proceeding anyway")
            except Exception as e:
                print(f"Could not verify checkbox state: {e} - proceeding anyway")
        else:
            print("✅ Follow company checkbox already unchecked")

    except Exception as e:
        print(f"Error handling follow company checkbox: {e} - continuing anyway")


def check_if_already_applied(text_content):
    """
    Check if job is already applied based on text content.
    Based on Chrome extension checkIfAlreadyApplied function.
    """
    if not text_content:
        return False

    text_lower = text_content.lower()
    already_applied_indicators = [
        "application sent",
        "applied",
        "you applied",
        "your application was sent",
        "application submitted",
    ]

    return any(indicator in text_lower for indicator in already_applied_indicators)
