#!/usr/bin/env python3
"""
Simple test script to verify Selenium connection
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Starting Selenium test...")

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    # Connect to remote Selenium server
    print("Connecting to Selenium Chrome...")
    driver = webdriver.Remote(
        command_executor='http://selenium-chrome:4444/wd/hub',
        options=chrome_options
    )
    
    # Navigate to a simple page
    print("Navigating to example.com...")
    driver.get("https://example.com")
    
    # Wait for page to load
    time.sleep(2)
    
    # Get page title
    title = driver.title
    print(f"Page title: {title}")
    
    # Get page content
    h1_text = driver.find_element(By.TAG_NAME, "h1").text
    print(f"H1 content: {h1_text}")
    
    # Take screenshot
    driver.save_screenshot("/opt/airflow/data/screenshots/test_screenshot.png")
    print("Screenshot saved to /opt/airflow/data/screenshots/test_screenshot.png")
    
    # Close browser
    driver.quit()
    print("Selenium test completed successfully!")
    
except Exception as e:
    print(f"Error during Selenium test: {e}")
    exit(1)
