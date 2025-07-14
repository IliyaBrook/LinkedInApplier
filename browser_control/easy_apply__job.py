import json
import time

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

from browser_control.browser_utils import (
    wait_for_elements,
    wait_for_element,
    wait_for_clickable_element,
    smart_delay,
    handle_save_application_modal,
    terminate_job_modal,
    close_all_modals,
)


def apply_to_job(driver, autofill_data):
    try:

        if handle_save_application_modal(driver):
            print("Save modal handled before starting application")
            return True

        already_applied_element = wait_for_element(
            driver, ".artdeco-inline-feedback__message", timeout=2
        )
        if already_applied_element:
            text_content = already_applied_element.text
            if check_if_already_applied(text_content):
                print(f"Already applied to this job: {text_content}")
                return True

        easy_apply_btn = None

        try:
            detail_section = driver.find_element(
                By.CSS_SELECTOR, ".scaffold-layout__detail"
            )
            print("Found scaffold-layout__detail section")
        except NoSuchElementException:
            print("scaffold-layout__detail section not found, searching in full page")
            detail_section = driver

        selectors = [
            "#jobs-apply-button-id",
            "button[aria-label*='Easy Apply']",
            ".jobs-apply-button",
            "button[class*='jobs-apply-button']",
            ".jobs-apply-button--top-card",
            "button[data-control-name='jobdetails_topcard_inapply']",
            "//button[contains(@aria-label, 'Easy Apply')]",
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
                        except (
                            NoSuchElementException,
                            StaleElementReferenceException,
                            WebDriverException,
                        ):
                            easy_apply_btn = None

                if easy_apply_btn:

                    aria_label = easy_apply_btn.get_attribute("aria-label") or ""
                    button_text = easy_apply_btn.text.strip()

                    print(
                        f"Found button with selector #{i+1}: aria-label='{aria_label}', text='{button_text}'"
                    )

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

            try:
                search_context = detail_section if detail_section != driver else driver
                all_buttons = search_context.find_elements(By.TAG_NAME, "button")
                print(f"Found {len(all_buttons)} buttons in detail section:")
                for btn in all_buttons[:10]:
                    try:
                        aria_label = btn.get_attribute("aria-label") or "No aria-label"
                        btn_class = btn.get_attribute("class") or "No class"
                        btn_text = btn.text.strip() or "No text"
                        btn_id = btn.get_attribute("id") or "No id"
                        print(
                            f"  Button: id='{btn_id}', aria-label='{aria_label}', class='{btn_class}', text='{btn_text}'"
                        )
                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                        AttributeError,
                    ):
                        pass
            except Exception as e:
                print(f"Could not debug buttons: {e}")

            return False

        print(f"Clicking Easy Apply button...")
        easy_apply_btn.click()
        smart_delay(2.0)

        print("Checking what appeared after clicking Easy Apply...")
        try:

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
                except (
                    StaleElementReferenceException,
                    WebDriverException,
                    AttributeError,
                ):
                    pass
        except Exception as e:
            print(f"Could not debug potential modals: {e}")

        max_iterations = 10
        iteration = 0

        print(f"Starting main application loop...")

        while iteration < max_iterations:

            if handle_save_application_modal(driver):
                print("Save modal handled during application process")
                return True

            modal_selectors = [
                ".artdeco-modal",
                "[data-test-modal]",
                ".jobs-easy-apply-modal",
                ".ember-application .ember-view .artdeco-modal",
                "[role='dialog']",
                ".artdeco-modal--layer-default",
            ]

            apply_modal = None

            for selector in modal_selectors:
                apply_modal = wait_for_element(driver, selector, timeout=3)
                if apply_modal:
                    print(f"Modal found with selector: {selector}")
                    break

            if not apply_modal:
                print(
                    f"No modal found with any selector after {iteration + 1} attempts"
                )

                try:
                    print("Debugging - looking for any modal-like elements:")
                    all_modals = driver.find_elements(
                        By.CSS_SELECTOR,
                        "[class*='modal'], [class*='dialog'], [role='dialog']",
                    )
                    print(f"Found {len(all_modals)} modal-like elements:")
                    for i, modal in enumerate(all_modals[:5]):
                        try:
                            classes = modal.get_attribute("class") or "No class"
                            role = modal.get_attribute("role") or "No role"
                            text_snippet = modal.text[:100] if modal.text else "No text"
                            print(
                                f"  Modal {i+1}: class='{classes}', role='{role}', text='{text_snippet}...'"
                            )
                        except (
                            StaleElementReferenceException,
                            WebDriverException,
                            AttributeError,
                        ):
                            pass
                except Exception as e:
                    print(f"Could not debug modals: {e}")

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

                if iteration >= 3:
                    print(
                        "No application modal found after multiple attempts - this might be an error"
                    )
                    return False

                smart_delay(2.0)
                iteration += 1
                continue

            print(f"Modal found! Processing application form...")

            form = None
            try:
                form = apply_modal.find_element(By.CSS_SELECTOR, "form")
                print(f"Form found in modal")
            except NoSuchElementException:
                print(f"No form found in modal")
                pass

            if not form:
                print("No form found in modal, checking for completion messages...")

                modal_text = apply_modal.text.lower()
                if any(
                    keyword in modal_text
                    for keyword in ["sent", "submitted", "complete", "thank you"]
                ):
                    print(f"Application appears to be complete based on modal text")
                    close_all_modals(driver)
                    return True

                is_final_step = check_if_final_step(driver, apply_modal)
                if is_final_step:
                    print(
                        "✅ Detected final step (100% progress) - looking for submit button even without form"
                    )
                else:
                    print(
                        "Not on final step yet, but checking for action buttons anyway..."
                    )

                print("Checking for action buttons without form...")
                next_action = find_next_action_button(driver, apply_modal)

                if next_action["type"] != "none":
                    print(f"Found action button without form: {next_action['type']}")

                else:
                    print(
                        "No action buttons found without form, continuing to next iteration..."
                    )
                    iteration += 1
                    continue

            form_updated = False
            if form:
                form_updated = process_form_fields(driver, form, autofill_data)
                print("Form fields processed")
            else:
                print("No form to process, skipping form field processing")

            if form_updated:

                with open("DB/form_autofill.json", "w", encoding="utf-8") as f:
                    json.dump(autofill_data, f, ensure_ascii=False, indent=2)

            next_action = find_next_action_button(driver, apply_modal)

            if next_action["type"] == "none":
                print(f"❌ No action button found in iteration {iteration + 1}")

                if iteration < 2:
                    print("Retrying button search after scrolling...")
                    try:

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

                        next_action = find_next_action_button(driver, apply_modal)

                        if next_action["type"] != "none":
                            print(f"✅ Found button after retry: {next_action['type']}")
                        else:
                            print("Still no button found after retry")
                    except Exception as e:
                        print(f"Error during retry: {e}")

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

                submit_button = next_action["element"]

                try:
                    driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;",
                        apply_modal,
                    )
                    smart_delay(1.0)
                    print("Scrolled to bottom of modal before submit")
                except (StaleElementReferenceException, WebDriverException, TypeError):
                    pass

                print("Unchecking follow company checkbox before submit...")
                uncheck_follow_company_checkbox(driver)

                print("Preparing to click Submit button...")
                try:

                    if not submit_button.is_displayed():
                        print("⚠️ Submit button is no longer displayed, re-finding...")
                        next_action = find_next_action_button(driver, apply_modal)
                        if next_action["type"] == "submit":
                            submit_button = next_action["element"]
                        else:
                            print("❌ Could not re-find submit button")
                            raise Exception("Submit button disappeared")

                    print("Scrolling to Submit button...")
                    for scroll_attempt in range(3):
                        try:
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                                submit_button,
                            )
                            smart_delay(1.0)

                            if submit_button.is_displayed():
                                print(
                                    f"✅ Submit button visible after scroll attempt {scroll_attempt + 1}"
                                )
                                break
                            else:
                                print(
                                    f"⚠️ Submit button not visible after scroll attempt {scroll_attempt + 1}"
                                )
                                if scroll_attempt < 2:

                                    driver.execute_script(
                                        "arguments[0].scrollIntoView(true);",
                                        submit_button,
                                    )
                                    smart_delay(0.5)
                        except Exception as e:
                            print(f"Error in scroll attempt {scroll_attempt + 1}: {e}")

                    is_enabled = submit_button.is_enabled()
                    is_displayed = submit_button.is_displayed()
                    print(
                        f"Submit button state: enabled={is_enabled}, displayed={is_displayed}"
                    )

                    if not is_enabled:
                        print("⚠️ Submit button is not enabled - waiting...")
                        smart_delay(2.0)
                        is_enabled = submit_button.is_enabled()
                        print(f"Submit button enabled after wait: {is_enabled}")

                    if not is_displayed:
                        print(
                            "⚠️ Submit button is not displayed - trying to scroll again..."
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", submit_button
                        )
                        smart_delay(1.0)

                    click_success = False

                    try:
                        print("Attempting regular click on Submit button...")
                        submit_button.click()
                        click_success = True
                        print("✅ Submit button clicked successfully (regular click)")
                    except Exception as e:
                        print(f"Regular click failed: {e}")

                    if not click_success:
                        try:
                            print("Attempting JavaScript click on Submit button...")
                            driver.execute_script(
                                "arguments[0].click();", submit_button
                            )
                            click_success = True
                            print(
                                "✅ Submit button clicked successfully (JavaScript click)"
                            )
                        except Exception as e:
                            print(f"JavaScript click failed: {e}")

                    if not click_success:
                        raise Exception("All click methods failed")

                    smart_delay(3.0)

                    if handle_save_application_modal(driver):
                        print("Save modal handled after submit")
                        return True

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
                    except WebDriverException:
                        pass

                    close_all_modals(driver)
                    return True

                except Exception as e:
                    print(f"Error clicking submit button: {e}")
                    close_all_modals(driver)
                    return False

            elif next_action["type"] == "next":
                print("Found next/review button, proceeding to next step")

                next_button = next_action["element"]

                try:
                    button_text = next_button.text.strip()
                    button_aria = (
                        next_button.get_attribute("aria-label") or "No aria-label"
                    )
                    next_button.get_attribute("class") or "No class"
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
                except (
                    StaleElementReferenceException,
                    WebDriverException,
                    AttributeError,
                ):
                    pass

                try:

                    print("Scrolling to Next/Review button...")
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        next_button,
                    )
                    smart_delay(1.0)

                    if not next_button.is_enabled():
                        print("⚠️ Next/Review button is not enabled, waiting...")
                        smart_delay(2.0)

                    if not next_button.is_displayed():
                        print("⚠️ Next/Review button is not visible after scroll")

                    print("Attempting to click Next/Review button...")
                    next_button.click()
                    print("✅ Next/Review button clicked successfully")
                    smart_delay(2.0)

                    if handle_save_application_modal(driver):
                        print("Save modal handled after next")
                        return True

                    discard_buttons = wait_for_elements(
                        driver, "button[data-test-dialog-secondary-btn]", timeout=2
                    )
                    for button in discard_buttons:
                        if "discard" in button.text.lower():
                            print("Discard button found, terminating application")
                            terminate_job_modal(driver)
                            return False

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
                    except WebDriverException:
                        pass

                except Exception as e:
                    print(f"❌ Error clicking next button: {e}")

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
                                except (
                                    StaleElementReferenceException,
                                    WebDriverException,
                                    AttributeError,
                                ):
                                    pass
                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                        AttributeError,
                    ):
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

            iteration += 1

        close_all_modals(driver)
        return True

    except Exception as e:
        print(f"Error in apply_to_job: {e}")
        try:
            close_all_modals(driver)
        except WebDriverException:
            pass
        return False


def process_form_fields(driver, form, autofill_data):
    """
    Process all form fields (inputs, radio buttons, dropdowns) in the given form.
    """
    updated = False

    if process_input_fields(form, autofill_data):
        updated = True

    if process_radio_buttons(driver, form, autofill_data):
        updated = True

    if process_dropdowns(driver, form, autofill_data):
        updated = True

    return updated


def process_input_fields(form, autofill_data):
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

            if tag == "input" and type_ == "checkbox":
                if not field.is_selected():
                    try:
                        field.click()
                        smart_delay(0.1)
                    except:
                        pass
                continue

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
                        print(f"Filled text input '{name}' with value: {autofill_val}")
                    except Exception as e:
                        print(f"Failed to fill text input '{name}': {e}")
                elif not autofill_val and name:
                    if db_section not in autofill_data:
                        autofill_data[db_section] = {}
                    if name not in autofill_data[db_section]:
                        autofill_data[db_section][name] = value or ""
                        updated = True
                        print(
                            f"Added new text input field to database: '{name}' = '{value or ''}'"
                        )
                elif name:
                    print(f"Text input '{name}' already has correct value: {value}")

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

                stored_selected_option = next(
                    (o for o in found["options"] if o["selected"]),
                    None,
                )

                if (
                    stored_selected_option
                    and stored_selected_option["value"] != selected_value
                ):

                    for radio in radios:
                        if (
                            radio.get_attribute("value")
                            == stored_selected_option["value"]
                        ):
                            try:
                                radio.click()
                                smart_delay(0.2)
                                print(
                                    f"Selected radio button: {stored_selected_option['value']} for {label}"
                                )
                                break
                            except Exception as e:
                                print(f"Failed to select radio button: {e}")
                elif not stored_selected_option:
                    print(f"No valid selection found for radio button group '{label}'")
                else:
                    print(
                        f"Radio button group '{label}' already has correct value: {selected_value}"
                    )

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

            label = get_dropdown_label(select)

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

                stored_selected_option = next(
                    (
                        o
                        for o in found["options"]
                        if o["selected"] and o["value"] != "Select an option"
                    ),
                    None,
                )

                if (
                    stored_selected_option
                    and stored_selected_option["value"] != selected_value
                ):

                    option_elements = select.find_elements(By.TAG_NAME, "option")
                    for option_elem in option_elements:
                        if (
                            option_elem.get_attribute("value")
                            == stored_selected_option["value"]
                        ):
                            try:
                                option_elem.click()
                                smart_delay(0.2)
                                print(
                                    f"Selected dropdown option: {stored_selected_option['value']} for {label}"
                                )
                                break
                            except Exception as e:
                                print(f"Failed to select dropdown option: {e}")
                elif not stored_selected_option:
                    print(
                        f"No valid selection found for dropdown '{label}' - still at 'Select an option'"
                    )
                else:
                    print(
                        f"Dropdown '{label}' already has correct value: {selected_value}"
                    )

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

    try:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;", modal
        )
        smart_delay(0.5)
        print("Scrolled to bottom of modal")
    except:
        pass

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

    submit_selectors = [
        'button[aria-label="Submit application"]',
        "button[data-live-test-easy-apply-submit-button]",
        'button[class*="artdeco-button--primary"]',
        "button.artdeco-button--primary",
        'button[type="button"][class*="artdeco-button--primary"]',
        "button.artdeco-button.artdeco-button--2.artdeco-button--primary",
        'button[class*="artdeco-button"][class*="artdeco-button--primary"][type="button"]',
    ]

    submit_xpath_selectors = [
        '//button[contains(text(), "Submit application")]',
        '//button[contains(text(), "Submit")]',
        '//button[contains(@aria-label, "Submit application")]',
        "//button[@data-live-test-easy-apply-submit-button]",
        '//button[contains(@class, "artdeco-button--primary") and contains(text(), "Submit")]',
        '//button[contains(@class, "artdeco-button--primary") and contains(@aria-label, "Submit")]',
    ]

    submit_btn = None

    for selector in submit_selectors:
        try:
            submit_btn = modal.find_element(By.CSS_SELECTOR, selector)
            if submit_btn and submit_btn.is_displayed():

                aria_label = submit_btn.get_attribute("aria-label") or ""
                button_text = submit_btn.text.strip()
                if "submit" in aria_label.lower() or "submit" in button_text.lower():
                    print(f"Found submit button with CSS selector: {selector}")
                    break
                else:
                    submit_btn = None
        except:
            continue

    if not submit_btn:
        for xpath_selector in submit_xpath_selectors:
            try:
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed():
                        submit_btn = elem
                        print(
                            f"Found submit button with XPath selector: {xpath_selector}"
                        )
                        break
                if submit_btn:
                    break
            except:
                continue

    if submit_btn:

        try:
            aria_label = submit_btn.get_attribute("aria-label") or "No aria-label"
            button_text = submit_btn.text.strip() or "No text"
            button_class = submit_btn.get_attribute("class") or "No class"
            button_id = submit_btn.get_attribute("id") or "No id"
            data_attr = (
                submit_btn.get_attribute("data-live-test-easy-apply-submit-button")
                or "No data-attr"
            )
            is_enabled = submit_btn.is_enabled()
            is_displayed = submit_btn.is_displayed()

            print(f"✅ Found Submit application button:")
            print(f"  - aria-label: '{aria_label}'")
            print(f"  - text: '{button_text}'")
            print(f"  - class: '{button_class}'")
            print(f"  - id: '{button_id}'")
            print(f"  - data-attr: '{data_attr}'")
            print(f"  - enabled: {is_enabled}")
            print(f"  - displayed: {is_displayed}")
        except Exception as e:
            print(f"Error getting submit button details: {e}")

        try:
            print("Scrolling to submit button...")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                submit_btn,
            )
            smart_delay(1.0)
            print("✅ Scrolled to Submit button")

            if not submit_btn.is_displayed():
                print(
                    "⚠️ Submit button not visible after scroll, trying alternative scroll"
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                smart_delay(0.5)
        except Exception as e:
            print(f"Error scrolling to submit button: {e}")

        return {"type": "submit", "element": submit_btn}

    review_css_selectors = [
        'button[aria-label="Review your application"]',
        'button[aria-label*="Review"]',
        "button[data-easy-apply-review-button]",
        "button[data-live-test-easy-apply-review-button]",
    ]

    review_xpath_selectors = [
        '//button[contains(text(), "Review")]',
        '//button[contains(@aria-label, "Review")]',
        "//button[@data-easy-apply-review-button]",
        "//button[@data-live-test-easy-apply-review-button]",
    ]

    review_btn = None

    for selector in review_css_selectors:
        try:
            review_btn = modal.find_element(By.CSS_SELECTOR, selector)
            if review_btn and review_btn.is_displayed():
                print(f"Found review button with CSS selector: {selector}")
                break
        except:
            continue

    if not review_btn:
        for xpath_selector in review_xpath_selectors:
            try:
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed():
                        review_btn = elem
                        print(
                            f"Found review button with XPath selector: {xpath_selector}"
                        )
                        break
                if review_btn:
                    break
            except:
                continue

    if review_btn:
        print(
            f"Found Review button: {review_btn.get_attribute('aria-label') or review_btn.text}"
        )

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

    next_css_selectors = [
        'button[aria-label="Continue to next step"]',
        "button[data-easy-apply-next-button]",
        "button[data-live-test-easy-apply-next-button]",
        'button[aria-label*="Next"]',
        'button[aria-label*="Continue"]',
        "button.artdeco-button--primary",
    ]

    next_xpath_selectors = [
        '//button[contains(text(), "Next")]',
        '//button[contains(@aria-label, "Next")]',
        '//button[contains(@aria-label, "Continue")]',
        "//button[@data-easy-apply-next-button]",
        "//button[@data-live-test-easy-apply-next-button]",
        '//button[contains(@class, "artdeco-button--primary") and contains(text(), "Next")]',
        '//button[contains(@class, "artdeco-button--primary") and contains(@aria-label, "Next")]',
        '//button[contains(@class, "artdeco-button--primary") and contains(@aria-label, "Continue")]',
    ]

    next_btn = None

    for selector in next_css_selectors:
        try:
            next_btn = modal.find_element(By.CSS_SELECTOR, selector)
            if next_btn and next_btn.is_displayed():
                print(f"Found next button with CSS selector: {selector}")
                break
        except:
            continue

    if not next_btn:
        for xpath_selector in next_xpath_selectors:
            try:
                elements = modal.find_elements(By.XPATH, xpath_selector)
                for elem in elements:
                    if elem.is_displayed():
                        next_btn = elem
                        print(
                            f"Found next button with XPath selector: {xpath_selector}"
                        )
                        break
                if next_btn:
                    break
            except:
                continue

    if next_btn:
        print(
            f"Found Next button: {next_btn.get_attribute('aria-label') or next_btn.text}"
        )

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
        print("🔍 Looking for follow company checkbox...")

        footer_section = None
        try:
            footer_section = driver.find_element(
                By.CSS_SELECTOR, ".job-details-easy-apply-footer__section"
            )
            print("✅ Found follow company footer section")
        except:
            print("⚠️ Follow company footer section not found, searching in full page")

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

        is_checked = follow_checkbox.is_selected()
        print(f"Follow company checkbox is {'checked' if is_checked else 'unchecked'}")

        if is_checked:
            print("Unchecking follow company checkbox...")

            scroll_target = footer_section if footer_section else follow_checkbox
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                scroll_target,
            )
            smart_delay(0.8)
            print("Scrolled to follow company section")

            if is_hidden or not follow_checkbox.is_displayed():
                print("Checkbox is visually hidden, looking for label to click...")
                try:

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

                print("Clicking visible checkbox...")
                follow_checkbox.click()
                smart_delay(0.5)

            smart_delay(0.3)
            try:
                is_still_checked = follow_checkbox.is_selected()
                if not is_still_checked:
                    print("✅ Successfully unchecked follow company checkbox")
                else:
                    print("⚠️ Checkbox might still be checked, trying one more time...")

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


def check_if_final_step(driver, modal):
    """
    Check if we're on the final step by looking for 100% progress indicator.
    Returns True if we're on the final step, False otherwise.
    """
    try:
        print("🔍 Checking if we're on the final step...")

        progress_selectors = [
            'progress[value="100"]',
            'progress[aria-valuenow="100"]',
            '.artdeco-completeness-meter-linear__progress-element[value="100"]',
            'progress[max="100"][value="100"]',
        ]

        search_contexts = [modal, driver]

        for context in search_contexts:
            for selector in progress_selectors:
                try:
                    progress_element = context.find_element(By.CSS_SELECTOR, selector)
                    if progress_element:
                        value = progress_element.get_attribute("value")
                        aria_valuenow = progress_element.get_attribute("aria-valuenow")
                        max_value = progress_element.get_attribute("max")

                        print(
                            f"Found progress element: value='{value}', aria-valuenow='{aria_valuenow}', max='{max_value}'"
                        )

                        if value == "100" or aria_valuenow == "100":
                            print("✅ Progress is at 100% - we're on the final step!")
                            return True
                except:
                    continue

        percentage_selectors = [
            'span[aria-label*="100 percent"]',
            'span:contains("100%")',
            '.t-14:contains("100%")',
        ]

        for context in search_contexts:
            for selector in percentage_selectors:
                try:
                    if ":contains(" in selector:

                        xpath_selector = '//span[contains(text(), "100%")]'
                        elements = context.find_elements(By.XPATH, xpath_selector)
                        for elem in elements:
                            if elem.is_displayed():
                                print(f"Found 100% text indicator: {elem.text}")
                                return True
                    else:
                        elem = context.find_element(By.CSS_SELECTOR, selector)
                        if elem and elem.is_displayed():
                            print(
                                f"Found 100% aria-label indicator: {elem.get_attribute('aria-label')}"
                            )
                            return True
                except:
                    continue

        print("No 100% progress indicator found - not on final step")
        return False

    except Exception as e:
        print(f"Error checking final step: {e}")
        return False


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
