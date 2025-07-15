from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scroll_to_element(
    driver: WebDriver,
    xpath: str,
    timeout: int = 10,
    scroll_behavior: str = "smooth",
    scroll_block: str = "center",
    scroll_inline: str = "nearest",
    pre_scroll_delay: float = 0.5,
    post_scroll_delay: float = 0.5,
):
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

        return element

    except Exception as e:
        print(f"Error scrolling to element '{xpath}': {e}")
        return None
