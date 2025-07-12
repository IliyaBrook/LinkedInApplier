import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def apply_to_job(driver, autofill_data):
    try:
        wait = WebDriverWait(driver, 20)
        easy_apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]")))
        easy_apply_btn.click()
        time.sleep(2)
        while True:
            form = None
            try:
                form = driver.find_element(By.CSS_SELECTOR, ".jobs-easy-apply-modal form")
            except Exception:
                pass
            if not form:
                break
            inputs = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            updated = False
            for field in inputs:
                name = field.get_attribute("name") or field.get_attribute("aria-label") or field.get_attribute("placeholder")
                value = field.get_attribute("value")
                tag = field.tag_name
                type_ = field.get_attribute("type")
                if tag == "input" and type_ in ("text", "email", "tel"):
                    db_section = "inputFieldConfigs"
                elif tag == "input" and type_ in ("radio",):
                    db_section = "radioButtons"
                elif tag == "select":
                    db_section = "dropdowns"
                else:
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
            if updated:
                with open("DB/form_autofill.json", "w", encoding="utf-8") as f:
                    json.dump(autofill_data, f, ensure_ascii=False, indent=2)
            next_btn = None
            try:
                next_btn = form.find_element(By.XPATH, ".//button[contains(., 'Next') or contains(., 'Review') or contains(., 'Submit')]")
            except Exception:
                pass
            if next_btn:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
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