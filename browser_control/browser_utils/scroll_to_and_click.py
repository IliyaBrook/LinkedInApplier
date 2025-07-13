from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scroll_to_and_click(
    driver: WebDriver,
    xpath: str,
    timeout: int = 5,
    scroll_behavior: str = "smooth",
    scroll_block: str = "center",
    scroll_inline: str = "nearest",
    pre_scroll_delay: float = 0.5,
    post_scroll_delay: float = 0.5,
    post_click_delay: float = 0.5,
) -> bool:
    """
    Finds element by XPath, scrolls to it and clicks.

    Args:
        driver (WebDriver): WebDriver object (e.g. Chrome, Firefox).
        xpath (str): XPath of element to find, scroll to and click.
        timeout (int): Maximum wait time (in seconds) for element to appear.
        scroll_behavior (str): How element should scroll into view.
                             Available values: 'auto', 'instant', 'smooth'.
        scroll_block (str): Vertical alignment.
                          Available values: 'start', 'center', 'end', 'nearest'.
        scroll_inline (str): Horizontal alignment.
                           Available values: 'start', 'center', 'end', 'nearest'.
        pre_scroll_delay (float): Delay before scrolling (in seconds).
        post_scroll_delay (float): Delay after scrolling (in seconds).
        post_click_delay (float): Delay after clicking element (in seconds).

    Returns:
        bool: True if element found and clicked successfully, False otherwise.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print(f"Element with XPath '{xpath}' found.")

        if pre_scroll_delay > 0:
            time.sleep(pre_scroll_delay)

        scroll_options = {
            "behavior": scroll_behavior,
            "block": scroll_block,
            "inline": scroll_inline,
        }
        driver.execute_script(
            "arguments[0].scrollIntoView(arguments[1]);", element, scroll_options
        )
        print(f"Scrolled to element '{xpath}' with options: {scroll_options}")

        if post_scroll_delay > 0:
            time.sleep(post_scroll_delay)

        clickable_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        print(f"Element with XPath '{xpath}' became clickable.")

        clickable_element.click()
        print(f"Click on element '{xpath}' successful.")

        if post_click_delay > 0:
            time.sleep(post_click_delay)

        return True

    except Exception as e:
        print(f"Error interacting with element '{xpath}': {e}")
        return False
