from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from .scroll_to_element import scroll_to_element


def scroll_to_and_click(
    driver: WebDriver,
    xpath: str,
    timeout: int = 10,
    scroll_behavior: str = "smooth",
    scroll_block: str = "center",
    scroll_inline: str = "nearest",
    pre_scroll_delay: float = 0.5,
    post_scroll_delay: float = 0.5,
    post_click_delay: float = 0.5,
) -> bool:
    try:
        # Use the new scroll_to_element function
        element = scroll_to_element(
            driver,
            xpath,
            timeout=timeout,
            scroll_behavior=scroll_behavior,
            scroll_block=scroll_block,
            scroll_inline=scroll_inline,
            pre_scroll_delay=pre_scroll_delay,
            post_scroll_delay=post_scroll_delay,
        )

        if element is None:
            print(f"Failed to find or scroll to element '{xpath}'.")
            return False

        # Wait for element to become clickable
        clickable_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        print(f"Element with XPath '{xpath}' became clickable.")

        # Click the element
        clickable_element.click()
        print(f"Click on element '{xpath}' successful.")

        # Delay after click
        if post_click_delay > 0:
            time.sleep(post_click_delay)

        return True

    except Exception as e:
        print(f"Error clicking element '{xpath}': {e}")
        return False
