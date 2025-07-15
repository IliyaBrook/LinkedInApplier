import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def wait_for_elements(driver, selector, timeout=5, by=By.CSS_SELECTOR, context=None):
    """
    Wait for elements to be present and visible on the page.
    Returns list of found elements or empty list if timeout.
    """
    try:
        if context is None:
            context = driver

        wait = WebDriverWait(context, timeout)
        elements = wait.until(EC.presence_of_all_elements_located((by, selector)))

        visible_elements = []
        for element in elements:
            try:
                if element.is_displayed() and element.is_enabled():
                    visible_elements.append(element)
            except:
                continue

        return visible_elements
    except TimeoutException:
        return []


def wait_for_element(driver, selector, timeout=5, by=By.CSS_SELECTOR, context=None):
    """
    Wait for a single element to be present and visible on the page.
    Returns element or None if timeout.
    """
    elements = wait_for_elements(driver, selector, timeout, by, context)
    return elements[0] if elements else None


def wait_for_clickable_element(
    driver, selector, timeout=5, by=By.CSS_SELECTOR, context=None
):
    """
    Wait for element to be clickable.
    Returns element or None if timeout.
    """
    try:
        if context is None:
            context = driver

        wait = WebDriverWait(context, timeout)
        element = wait.until(EC.element_to_be_clickable((by, selector)))
        return element
    except TimeoutException:
        return None


def smart_delay(base_delay=0.5, max_delay=1.0):
    """
    Smart delay function that varies the delay time slightly.
    """
    import random

    actual_delay = base_delay + (random.random() * (max_delay - base_delay))
    time.sleep(actual_delay)
