import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def apply_to_job(driver, autofill_data):
    try:
        wait = WebDriverWait(driver, 20)
        easy_apply_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]",
                )
            )
        )
        easy_apply_btn.click()
        time.sleep(2)
        while True:
            form = None
            try:
                form = driver.find_element(
                    By.CSS_SELECTOR, ".jobs-easy-apply-modal form"
                )
            except Exception:
                pass
            if not form:
                break
            updated = False
            # --- INPUT FIELDS ---
            inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea")
            for field in inputs:
                tag = field.tag_name
                type_ = field.get_attribute("type")
                name = (
                    field.get_attribute("name")
                    or field.get_attribute("aria-label")
                    or field.get_attribute("placeholder")
                )
                value = field.get_attribute("value")
                if tag == "input" and type_ in ("text", "email", "tel"):
                    db_section = "inputFieldConfigs"
                    val = autofill_data.get(db_section, {}).get(name, "")
                    if val:
                        try:
                            field.clear()
                        except Exception:
                            pass
                        field.send_keys(val)
                    else:
                        if db_section not in autofill_data:
                            autofill_data[db_section] = {}
                        if name and name not in autofill_data[db_section]:
                            autofill_data[db_section][name] = ""
                            updated = True
            # --- RADIO BUTTONS ---
            radio_fieldsets = form.find_elements(
                By.CSS_SELECTOR,
                'fieldset[data-test-form-builder-radio-button-form-component="true"]',
            )
            for fieldset in radio_fieldsets:
                legend = fieldset.find_element(By.TAG_NAME, "legend")
                label_el = (
                    legend.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"]')
                    if legend
                    else None
                )
                label = label_el.text.strip() if label_el else legend.text.strip()
                options = []
                radios = fieldset.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                selected_value = None
                for radio in radios:
                    radio_label = ""
                    try:
                        radio_label_el = fieldset.find_element(
                            By.CSS_SELECTOR, f'label[for="{radio.get_attribute("id")}"]'
                        )
                        radio_label = radio_label_el.text.strip()
                    except Exception:
                        pass
                    if not radio_label:
                        parent = radio.find_element(By.XPATH, "..")
                        spans = parent.find_elements(By.TAG_NAME, "span")
                        for s in spans:
                            t = s.text.strip()
                            if t:
                                radio_label = t
                                break
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
                        if rb["placeholderIncludes"] == label
                    ),
                    None,
                )
                if not found:
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
                else:
                    found["options"] = options
                    if selected_value:
                        found["defaultValue"] = selected_value
                    found["count"] += 1
            # --- DROPDOWNS ---
            selects = form.find_elements(By.TAG_NAME, "select")
            for select in selects:
                parent = select.find_element(
                    By.XPATH, "ancestor::div[contains(@class, 'fb-dash-form-element')]"
                )
                label_el = parent.find_element(By.TAG_NAME, "label") if parent else None
                label = ""
                if label_el:
                    aria_hidden = None
                    try:
                        aria_hidden = label_el.find_element(
                            By.CSS_SELECTOR, 'span[aria-hidden="true"]'
                        )
                    except Exception:
                        pass
                    label = (
                        aria_hidden.text.strip()
                        if aria_hidden
                        else label_el.text.strip()
                    )
                if not label:
                    label = f"Dropdown {int(time.time())}"
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
                        if d["placeholderIncludes"] == label
                    ),
                    None,
                )
                if not found:
                    autofill_data["dropdowns"].append(
                        {
                            "placeholderIncludes": label,
                            "count": 1,
                            "options": options,
                            "defaultValue": selected_value,
                        }
                    )
                    updated = True
                else:
                    found["options"] = options
                    found["defaultValue"] = selected_value
                    found["count"] += 1
            if updated:
                with open("DB/form_autofill.json", "w", encoding="utf-8") as f:
                    json.dump(autofill_data, f, ensure_ascii=False, indent=2)
            next_btn = None
            try:
                next_btn = form.find_element(
                    By.XPATH,
                    ".//button[contains(., 'Next') or contains(., 'Review') or contains(., 'Submit')]",
                )
            except Exception:
                pass
            if next_btn:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", next_btn
                )
                next_btn.click()
                time.sleep(2)
            else:
                break
        try:
            close_btn = driver.find_element(By.CSS_SELECTOR, ".artdeco-modal__dismiss")
            close_btn.click()
        except Exception:
            pass
    except Exception as e:
        print("Error in apply_to_job:", e)
        return False
