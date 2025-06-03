#!/usr/bin/env python3
"""
Direct scraper for Assam tenders data.
This script uses a more direct approach to scraping, with better error handling.
"""

import os
import sys
import time
import base64
import logging
import argparse
from datetime import datetime, timedelta

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Import improved CAPTCHA utils
from captcha_utils import process_captcha, refresh_captcha

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('direct_scraper')

def wait_for_element(driver, by, value, timeout=10, condition=EC.presence_of_element_located):
    """Wait for an element to be present and return it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            condition((by, value))
        )
        return element
    except Exception as e:
        logger.error(f"Error waiting for element {value}: {e}")
        return None

def safe_click(driver, element):
    """Safely click an element using JavaScript if normal click fails."""
    try:
        element.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False

def safe_select_option(driver, select_element, value, by_value=True):
    """Safely select an option from a dropdown."""
    try:
        select = Select(select_element)
        if by_value:
            select.select_by_value(value)
        else:
            select.select_by_visible_text(value)
        return True
    except Exception as e:
        try:
            # Try using JavaScript as a fallback
            if by_value:
                driver.execute_script(
                    f"arguments[0].value = '{value}'; arguments[0].dispatchEvent(new Event('change'));", 
                    select_element
                )
            else:
                options = select_element.find_elements(By.TAG_NAME, "option")
                for option in options:
                    if option.text == value:
                        driver.execute_script("arguments[0].selected = true; arguments[0].dispatchEvent(new Event('change'));", option)
                        break
            return True
        except Exception as e2:
            logger.error(f"Error selecting option: {e} / {e2}")
            return False

def select_date(driver, date_field_id, target_date):
    """
    Select a date in the date picker with better error handling.
    
    Args:
        driver: Selenium WebDriver
        date_field_id: ID of the date field (e.g., 'fromDate' or 'toDate')
        target_date: Date to select as a datetime object
    """
    try:
        # Click on the date field to open the picker
        date_field = wait_for_element(driver, By.ID, date_field_id, condition=EC.element_to_be_clickable)
        if not date_field:
            logger.error(f"Could not find date field with ID: {date_field_id}")
            return False
            
        if not safe_click(driver, date_field):
            logger.error(f"Could not click on date field: {date_field_id}")
            return False
            
        time.sleep(1)
        
        # Find which date picker div is visible
        picker_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "datepicker")]')
        visible_picker = None
        for div in picker_divs:
            if div.is_displayed():
                visible_picker = div
                break
        
        if not visible_picker:
            logger.error(f"Could not find visible date picker for {date_field_id}")
            # Try to click outside to close any open pickers
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
            return False
        
        # Try multiple approaches to select the date
        try:
            # Approach 1: Use the month and year dropdowns if available
            month_dropdowns = visible_picker.find_elements(By.XPATH, './/select[contains(@class, "datepicker-month")]')
            year_dropdowns = visible_picker.find_elements(By.XPATH, './/select[contains(@class, "datepicker-year")]')
            
            if month_dropdowns and year_dropdowns:
                month_dropdown = month_dropdowns[0]
                year_dropdown = year_dropdowns[0]
                
                # Select month and year
                safe_select_option(driver, month_dropdown, str(target_date.month - 1))  # Month index is 0-based
                safe_select_option(driver, year_dropdown, str(target_date.year))
                time.sleep(1)  # Wait for calendar to update
            else:
                logger.warning(f"Could not find month/year dropdowns for {date_field_id}")
        except Exception as e:
            logger.warning(f"Error selecting month/year: {e}")
        
        # Try to find and click on the day
        try:
            # Find all available days
            day_cells = visible_picker.find_elements(By.XPATH, './/td[contains(@class, "day") and not(contains(@class, "disabled"))]')
            
            if not day_cells:
                logger.warning(f"No day cells found for {date_field_id}")
                # Try to click outside to close the picker
                driver.find_element(By.TAG_NAME, "body").click()
                return False
                
            # Try to find the exact day
            day_found = False
            for cell in day_cells:
                if cell.text.strip() == str(target_date.day):
                    if safe_click(driver, cell):
                        day_found = True
                        logger.info(f"Selected day {target_date.day} for {date_field_id}")
                        break
            
            # If exact day not found, select the middle day
            if not day_found:
                middle_day = day_cells[len(day_cells) // 2]
                if safe_click(driver, middle_day):
                    logger.info(f"Selected alternative day {middle_day.text} for {date_field_id}")
                else:
                    logger.error(f"Could not click on any day for {date_field_id}")
                    return False
            
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error selecting day: {e}")
            # Try to click outside to close the picker
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
            return False
    except Exception as e:
        logger.error(f"Error in date selection for {date_field_id}: {e}")
        return False

def handle_captcha_automatically(driver):
    """
    Handle CAPTCHA automatically by finding the image, processing it, and entering the text.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        bool: True if CAPTCHA was handled, False otherwise
    """
    logger.info("Starting automatic CAPTCHA handling")
    
    # Find CAPTCHA image using multiple detection methods
    captcha_img = None
    detection_methods = [
        # Method 1: By ID
        (By.ID, "captchaImage"),
        # Method 2: By common CAPTCHA-related IDs
        (By.CSS_SELECTOR, "img[id*='captcha' i], img[id*='verification' i]"),
    ]
    
    try:
        # Try each detection method
        for method, selector in detection_methods:
            try:
                elements = driver.find_elements(method, selector)
                visible_elements = [e for e in elements if e.is_displayed()]
                if visible_elements:
                    captcha_img = visible_elements[0]
                    logger.info(f"Found CAPTCHA image using method: {method} with selector: {selector}")
                    break
            except Exception:
                continue

        if not captcha_img:
            logger.error("Could not find CAPTCHA image")
            return False
            
        captcha_input = wait_for_element(driver, By.ID, "captchaText", timeout=5)
        if not captcha_input:
            # Try alternate IDs
            captcha_input = wait_for_element(driver, By.ID, "captchaText", timeout=5)
            if not captcha_input:
                logger.error("Could not find CAPTCHA input field")
                return False
        
        captcha_text = process_captcha(driver, "//img[contains(@id, 'captcha')]", "#captchaText")
        
        if not captcha_text:
            # Try refreshing CAPTCHA and processing again   
            if refresh_captcha(driver):
                time.sleep(1)  # Wait for new CAPTCHA to load
                captcha_text = process_captcha(driver, "//img[contains(@id, 'captcha')]", "#captchaText")
                
        if captcha_text:
            # Enter the CAPTCHA text
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            logger.info(f"Entered CAPTCHA text: {captcha_text}")
            return True
        else:
            logger.error("Could not process CAPTCHA")
            return False
            
    except Exception as e:
        logger.error(f"Error handling CAPTCHA: {e}")
        return False

# Keep the manual function as a fallback
def handle_captcha_manually(driver):
    """Fallback function for manual CAPTCHA handling."""
    try:
        captcha_input = wait_for_element(driver, By.ID, "captchaText", timeout=5)
        if not captcha_input:
            logger.error("Could not find CAPTCHA input field")
            return False
        
        logger.info("Please enter the CAPTCHA text manually")
        time.sleep(30)  # Wait for manual input
        return True
    except Exception as e:
        logger.error(f"Error in manual CAPTCHA handling: {e}")
        return False



def scrape_tenders(output_path, from_date, to_date, headless=True, max_retries=3):
    """
    Scrape tenders from the Assam tenders website with better error handling.
    
    Args:
        output_path: Path to save the output data
        from_date: Start date for scraping (YYYY-MM-DD)
        to_date: End date for scraping (YYYY-MM-DD)
        headless: Whether to run in headless mode
        max_retries: Maximum number of retries for operations
    
    Returns:
        bool: True if successful, False otherwise
    """
    driver = None
    try:
        # Convert dates to datetime objects
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
        
        # Set up Chrome options
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--ignore-certificate-errors')
        
        # Set up unhandled prompt behavior
        options.set_capability('unhandledPromptBehavior', 'accept')
        
        # Set up download preferences
        prefs = {
            "download.default_directory": os.path.abspath(output_path),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Connect to the remote Selenium service
        logger.info("Connecting to Selenium service...")
        
        for attempt in range(max_retries):
            try:
                driver = webdriver.Remote(
                    command_executor='http://selenium-chrome:4444/wd/hub',
                    options=options
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to Selenium service (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to connect to Selenium service after {max_retries} attempts: {e}")
                    return False
        
        # Navigate to the website - go directly to the tender search by location page
        url = "https://assamtenders.gov.in/nicgep/app?page=FrontEndTendersByLocation&service=page"
        logger.info(f"Navigating directly to tender search by location page: {url}...")
        
        for attempt in range(max_retries):
            try:
                driver.get(url)
                time.sleep(5)  # Wait longer for page to load
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to navigate to URL (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to navigate to URL after {max_retries} attempts: {e}")
                    return False
        
        # Save a screenshot to see where we are
        driver.save_screenshot("/tmp/initial_page.png")
        logger.info("Saved screenshot of initial page to /tmp/initial_page.png")
        
        # We should now be on the tender search by location page
        # Let's check if there's a location field to fill in
        try:
            # Look for any input field that might be for location
            input_fields = driver.find_elements(By.XPATH, "//input[@type='text']")
            location_field_found = False
            
            for field in input_fields:
                try:
                    placeholder = field.get_attribute("placeholder")
                    name = field.get_attribute("name")
                    id_attr = field.get_attribute("id")
                    
                    logger.info(f"Found input field - placeholder: {placeholder}, name: {name}, id: {id_attr}")
                    
                    # Check if this looks like a location field
                    if (placeholder and "city" in placeholder.lower()) or \
                       (name and "location" in name.lower()) or \
                       (id_attr and "location" in id_attr.lower()):
                        field.clear()
                        field.send_keys("Assam")
                        location_field_found = True
                        logger.info("Entered 'Assam' in location field")
                        time.sleep(1)
                        break
                except Exception as e:
                    logger.warning(f"Error checking input field: {e}")
            
            if not location_field_found:
                logger.warning("Could not find a location input field")
        except Exception as e:
            logger.warning(f"Error looking for location fields: {e}")
        
        # Take another screenshot after attempting to fill location
        driver.save_screenshot("/tmp/after_location_input.png")
        logger.info("Saved screenshot after location input to /tmp/after_location_input.png")
        
        # Wait a bit for the page to fully load
        time.sleep(2)
        
        # Take a screenshot before looking for CAPTCHA
        driver.save_screenshot("/tmp/before_captcha_search.png")
        logger.info("Saved screenshot before CAPTCHA search")
        
        # Handle CAPTCHA before searching - try multiple ways to find it
        captcha_img = None
        
        # Method 1: Try by ID first (from the HTML source)
        try:
            captcha_img_elements = driver.find_elements(By.ID, "captchaImage")
            if captcha_img_elements:
                captcha_img = captcha_img_elements[0]
                logger.info("Found CAPTCHA image by ID 'captchaImage'")
        except Exception as e:
            logger.warning(f"Error finding CAPTCHA by ID: {e}")
        
        # Method 2: Try by name
        if not captcha_img:
            try:
                captcha_img_elements = driver.find_elements(By.NAME, "captchaImage")
                if captcha_img_elements:
                    captcha_img = captcha_img_elements[0]
                    logger.info("Found CAPTCHA image by name 'captchaImage'")
            except Exception as e:
                logger.warning(f"Error finding CAPTCHA by name: {e}")
        
        # Method 3: Try by XPath looking for any image with 'captcha' in attributes
        if not captcha_img:
            try:
                xpath_patterns = [
                    "//img[contains(@src, 'captcha')]",
                    "//img[contains(@id, 'captcha')]",
                    "//img[contains(@name, 'captcha')]",
                    "//img[contains(@class, 'captcha')]",
                    "//td//img[contains(@src, 'data:image')]"
                ]
                
                for xpath in xpath_patterns:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        captcha_img = elements[0]
                        logger.info(f"Found CAPTCHA image using XPath: {xpath}")
                        break
            except Exception as e:
                logger.warning(f"Error finding CAPTCHA by XPath: {e}")
        
        # Method 4: Try to find by looking at page source
        if not captcha_img:
            try:
                page_source = driver.page_source
                if 'captchaImage' in page_source:
                    logger.info("Found 'captchaImage' in page source, but couldn't locate element")
                    # Log the relevant part of the source for debugging
                    start_idx = page_source.find('captchaImage')
                    context = page_source[max(0, start_idx-100):min(len(page_source), start_idx+100)]
                    logger.info(f"Page source context: {context}")
            except Exception as e:
                logger.warning(f"Error checking page source: {e}")
        
        if captcha_img:
            logger.info("Found CAPTCHA image, handling it automatically")
            try:
                # First try automatic CAPTCHA handling
                if handle_captcha_automatically(driver):
                    logger.info("Successfully handled CAPTCHA automatically")
                else:
                    # Fall back to manual handling if automatic fails
                    logger.warning("Automatic CAPTCHA handling failed, falling back to manual")
                    if not handle_captcha_manually(driver):
                        logger.error("Failed to handle CAPTCHA manually")
                        return False
            except Exception as e:
                logger.error(f"Error in CAPTCHA handling: {e}")
                # Fall back to manual handling
                logger.warning("Exception in automatic CAPTCHA handling, falling back to manual")
                if not handle_captcha_manually(driver):
                    logger.error("Failed to handle CAPTCHA manually")
                    return False
        else:
            # Take another screenshot to help debug why CAPTCHA wasn't found
            driver.save_screenshot("/tmp/captcha_not_found.png")
            logger.warning("No CAPTCHA image found - saved screenshot to /tmp/captcha_not_found.png")
            
            # Log the page source for debugging
            with open("/tmp/page_source.html", "w") as f:
                f.write(driver.page_source)
            logger.warning("Saved page source to /tmp/page_source.html")
            
            # Check if we're on the right page
            try:
                title = driver.title
                current_url = driver.current_url
                logger.info(f"Current page title: {title}")
                logger.info(f"Current URL: {current_url}")
            except Exception as e:
                logger.warning(f"Error getting page info: {e}")
            
        # Save a screenshot after handling CAPTCHA
        driver.save_screenshot("/tmp/after_captcha.png")
        logger.info("Saved screenshot after handling CAPTCHA to /tmp/after_captcha.png")
        
        # Find the Submit button - from the HTML source, it's input with id='submit' and name='submit'
        search_button = None
        
        # Try to find the submit button using the exact attributes from the HTML source
        button_selectors = [
            (By.ID, "submit"),  # From HTML: <input type="submit" name="submit" id="submit" border="0" onClick="return searchBox();" title="Submit" class="customButton" value="Submit" />
            (By.NAME, "submit"),
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//input[@value='Submit']"),
            (By.XPATH, "//input[@class='customButton']"),
            # More generic fallbacks
            (By.XPATH, "//input[@type='submit' or @type='button'][contains(@value, 'Submit')]"),
            (By.XPATH, "//button[contains(text(), 'Submit')]"),
            # From the HTML, there's a Cancel link next to the Submit button
            (By.XPATH, "//a[@id='cancel']/following-sibling::input")
        ]
        
        for selector_type, selector in button_selectors:
            elements = driver.find_elements(selector_type, selector)
            if elements:
                for element in elements:
                    try:
                        if element.is_displayed():
                            search_button = element
                            logger.info(f"Found submit button using selector: {selector}")
                            break
                    except Exception as e:
                        logger.warning(f"Error checking element visibility: {e}")
                        continue
                if search_button:
                    break
        
        # Take a screenshot of the form before submission
        driver.save_screenshot("/tmp/before_submit.png")
        logger.info("Saved screenshot before form submission to /tmp/before_submit.png")
        
        if not search_button:
            logger.error("Could not find search button")
            return False
            
        # Try multiple methods to click the submit button
        click_success = False
        
        # Method 1: Regular click
        try:
            logger.info("Trying regular click on submit button")
            search_button.click()
            time.sleep(2)
            click_success = True
            logger.info("Regular click on submit button succeeded")
        except Exception as e:
            logger.warning(f"Regular click failed: {e}")
        
        # Method 2: JavaScript click if regular click fails
        if not click_success:
            try:
                logger.info("Trying JavaScript click on submit button")
                driver.execute_script("arguments[0].click();", search_button)
                time.sleep(2)
                click_success = True
                logger.info("JavaScript click on submit button succeeded")
            except Exception as e:
                logger.warning(f"JavaScript click failed: {e}")
        
        # Method 3: Submit the form directly if button clicks fail
        if not click_success:
            try:
                logger.info("Trying to submit the form directly")
                # Find the form that contains the submit button
                form = driver.find_element(By.ID, "TendersbyLocation")
                form.submit()
                time.sleep(2)
                click_success = True
                logger.info("Form submission succeeded")
            except Exception as e:
                logger.warning(f"Form submission failed: {e}")
        
        if not click_success:
            logger.error("All methods to submit the form failed")
            return False
            
        time.sleep(3)
        logger.info("Form submitted successfully")
        
        # Take a screenshot after submission
        driver.save_screenshot("/tmp/after_submit.png")
        logger.info("Saved screenshot after form submission to /tmp/after_submit.png")
        
        # Save a screenshot after search
        driver.save_screenshot("/tmp/after_search.png")
        logger.info("Saved screenshot after search to /tmp/after_search.png")
        
        # Check if we're on the tender search results page or the search form page
        # Save a screenshot to see where we are
        driver.save_screenshot("/tmp/after_initial_search.png")
        
        # Check for the tender status dropdown which indicates we're on the search form
        status_dropdowns = driver.find_elements(By.ID, "tenderStatus")
        
        if status_dropdowns:
            logger.info("Found tender status dropdown, we're on the search form page")
            
            # Select tender status
            status_dropdown = status_dropdowns[0]
            if not safe_select_option(driver, status_dropdown, "6"):
                logger.warning("Could not select tender status, trying to continue")
            else:
                time.sleep(1)
                logger.info("Selected tender status")
            
            # Select from date
            if not select_date(driver, "fromDate", from_date_obj):
                logger.warning("Failed to select from date, continuing anyway")
            
            # Select to date
            if not select_date(driver, "toDate", to_date_obj):
                logger.warning("Failed to select to date, continuing anyway")
            
            # Handle CAPTCHA if present
            captcha_images = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
            if captcha_images:
                logger.info("Found CAPTCHA on the search form page")
                if not handle_captcha_manually(driver):
                    logger.error("Failed to handle CAPTCHA")
                    return False
            else:
                logger.info("No CAPTCHA found on the search form page")
            
            # Find and click the search button
            search_button = None
            for button_id in ["Search", "submit", "Submit"]:
                search_buttons = driver.find_elements(By.ID, button_id)
                if search_buttons:
                    search_button = search_buttons[0]
                    break
            
            if not search_button:
                # Try by value
                for button_value in ["Search", "Submit", "Go"]:
                    search_buttons = driver.find_elements(By.XPATH, f"//input[@value='{button_value}']")
                    if search_buttons:
                        search_button = search_buttons[0]
                        break
            
            if search_button:
                if not safe_click(driver, search_button):
                    logger.error("Could not click on search button")
                    return False
                time.sleep(3)
                logger.info("Clicked on search button after filling the form")
            else:
                logger.error("Could not find search button on the form")
                return False
        else:
            logger.info("No tender status dropdown found, we might already be on the results page")
        
            logger.warning("No tender results found")
            return False
        
        # Create a CSV file for the results
        csv_path = os.path.join(output_path, f"tender_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(csv_path, 'w') as f:
            # Write header
            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
            header = [cell.text.strip() for cell in header_cells]
            f.write(','.join([f'"{h}"' for h in header]) + '\n')
            
            # Write data rows
            for i in range(1, len(rows)):
                cells = rows[i].find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                f.write(','.join([f'"{d}"' for d in row_data]) + '\n')
        
        logger.info(f"Saved tender results to {csv_path}")
        return True
    except Exception as e:
        logger.error(f"Error in scraper: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

def main():
    
    parser = argparse.ArgumentParser(description='Direct scraper for Assam tenders data')
    parser.add_argument('--output-path', type=str, default='/opt/airflow/data/raw', help='Path to save the scraped data')
    parser.add_argument('--from-date', type=str, default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), help='Start date for scraping (YYYY-MM-DD)')
    parser.add_argument('--to-date', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='End date for scraping (YYYY-MM-DD)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()
    
    logger.info(f"Starting scraper with dates: {args.from_date} to {args.to_date}")
    success = scrape_tenders(args.output_path, args.from_date, args.to_date, args.headless)
    
    if success:
        logger.info("Scraping completed successfully")
        return 0
    else:
        logger.error("Scraping failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
