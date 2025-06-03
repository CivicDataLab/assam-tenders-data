import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def create_selenium_driver():
    """
    Create a Selenium WebDriver connected to the standalone Chrome container.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Comment this line if you need to see the browser via VNC
    chrome_options.add_argument("--headless")
    
    # Connect to the Selenium standalone Chrome container
    driver = webdriver.Remote(
        command_executor='http://selenium-chrome:4444/wd/hub',
        options=chrome_options
    )
    return driver

def get_page_element(driver, xpath=None, timeout=30):
    """
    Get a page element by XPath with explicit wait.
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath to the element
        timeout: Maximum time to wait in seconds
    
    Returns:
        Web element
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except TimeoutException:
        print(f"Timeout waiting for element: {xpath}")
        return None

def input_text_box(driver, element, text=None):
    """
    Input text into an input box.
    
    Args:
        driver: Selenium WebDriver instance
        element: Web element to input text into
        text: Text to input
    """
    element.clear()
    element.send_keys(text)

def wait_and_click(driver, xpath, timeout=30):
    """
    Wait for an element to be clickable and then click it.
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath to the element
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if click was successful, False otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        return True
    except TimeoutException:
        print(f"Timeout waiting for element to be clickable: {xpath}")
        return False

def save_screenshot(driver, filename=None):
    """
    Save a screenshot to the data directory.
    
    Args:
        driver: Selenium WebDriver instance
        filename: Name for the screenshot file
    
    Returns:
        Path to the saved screenshot
    """
    if filename is None:
        filename = f"screenshot_{int(time.time())}.png"
    
    screenshot_dir = "/opt/airflow/data/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    filepath = os.path.join(screenshot_dir, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved to {filepath}")
    return filepath

def scroll_to_element(driver, element):
    """
    Scroll to make an element visible.
    
    Args:
        driver: Selenium WebDriver instance
        element: Web element to scroll to
    """
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Allow time for scrolling animation