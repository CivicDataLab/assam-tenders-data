import time
import os
import warnings
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Import custom modules
# Using direct import instead of airflow.include prefix
import sys
import os

# Add the include directory to the Python path
include_dir = os.path.dirname(os.path.abspath(__file__))
if include_dir not in sys.path:
    sys.path.append(include_dir)

from scraper_utils import (
    select_date_from_picker, get_page_element, input_text_box,
    extract_vertical_table, extract_horizontal_table, concatinate_csvs,
    remove_csvs, get_multiple_page_elements, select_drop_down
)
from captcha_utils import process_captcha, check_captcha_and_reload

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Dictionary of table types for different sections
dict_tables_type = {
    "Bids List": "Vertical", 
    "Technical Bid Opening Summary": "Horizontal",
    "Technical Evaluation Summary Details": "Horizontal",
    "Bid Opening Summary": "Horizontal",
    "Finance Bid Opening Summary": "Horizontal",
    "Financial Evaluation Bid List": "Vertical",
    "Finance Evaluation Summary Details": "Horizontal",
    "AOC": "Horizontal",
    "Awarded Bids List": "Vertical",
    "Tender Revocation List": "Vertical",
    "Corrigendum Details": "Vertical"
}

def scrape_view_more_details(driver, tender_id):
    """
    Scrape the 'View More Details' section of a tender.
    
    :param driver: Selenium WebDriver instance
    :param tender_id: ID of the tender being scraped
    """
    try:
        # Click on the 'View More Details' button
        view_more_details_button = driver.find_element(By.XPATH, '//*[@id="viewMoreDetailsbtn"]')
        view_more_details_button.click()
        
        # Wait for the details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="viewMoreDetails"]'))
        )
        
        # Extract the details
        details_section = driver.find_element(By.XPATH, '//*[@id="viewMoreDetails"]')
        extract_vertical_table(details_section, "View_More_Details_" + tender_id, 0)
        
    except Exception as e:
        print(f"Error in scrape_view_more_details: {str(e)}")

def scrape_view_stage_summary(driver, tender_id, dict_tables_type):
    """
    Scrape the 'View Stage Summary' section of a tender.
    
    :param driver: Selenium WebDriver instance
    :param tender_id: ID of the tender being scraped
    :param dict_tables_type: Dictionary mapping table names to their types
    """
    try:
        # Click on the 'View Stage Summary' button
        view_stage_summary_button = driver.find_element(By.XPATH, '//*[@id="viewStageSummarybtn"]')
        view_stage_summary_button.click()
        
        # Wait for the summary to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "viewStageSummary"))
        )
        
        # Get all sections in the summary
        sections = []
        
        # Try to find sections by ID
        try:
            summary_section = driver.find_element(By.ID, "viewStageSummary")
            sections.append(summary_section)
        except NoSuchElementException:
            print("Element with ID 'viewStageSummary' not found")
        
        try:
            table_list_element = driver.find_element(By.ID, "table_list")
            sections.append(table_list_element)
        except NoSuchElementException:
            print("Element with ID 'table_list' not found")
        
        try:
            list_table_element = driver.find_element(By.CLASS_NAME, "list_table")
            sections.append(list_table_element)
        except NoSuchElementException:
            print("Element with CLASS_NAME 'list_table' not found")
        
        # Process each section
        for index, section in enumerate(sections):
            try:
                # Get the header name from the section
                header_elements = section.find_elements(By.CLASS_NAME, "section_head")
                header_name = header_elements[0].text if header_elements else "Unknown Section"
                
                # Process table data based on header name
                if header_name in dict_tables_type:
                    if dict_tables_type[header_name] == "Vertical":
                        extract_vertical_table(section, header_name + "_" + tender_id, 1)
                    else:
                        extract_horizontal_table(section, header_name + "_" + tender_id, 1)
                else:
                    # Default action for sections not in dict_tables_type
                    extract_horizontal_table(section, header_name + "_" + tender_id, 1)
            except Exception as e:
                print(f"Error processing section {index}: {e}")
        
        # Concatenate all CSV files
        os.makedirs("concatinated_csvs", exist_ok=True)
        concatinate_csvs("concatinated_csvs/", "summary" + "_" + tender_id)
        
    except Exception as e:
        print(f"Error in scrape_view_stage_summary: {str(e)}")

def get_table_links(driver, table_xpath):
    """
    Get links and tender IDs from a table.
    
    :param driver: Selenium WebDriver instance
    :param table_xpath: XPath to the table element
    :return: Table element, list of links, next page link, and list of tender IDs
    """
    table = get_page_element(driver, table_xpath)
    elements_list = table.find_elements(By.CSS_SELECTOR, "a")
    links = [element.get_attribute("href") for element in elements_list]
    rows = table.find_elements(By.CSS_SELECTOR, "tr")
    tender_ids = [row.find_element(By.XPATH, "td[2]").text for row in rows[1:-2]]

    # Check if the "loadNext" button exists before trying to access it
    next_page_elements = table.find_elements(By.XPATH, '//*[@id="loadNext"]')
    if next_page_elements:
        next_page_link = next_page_elements[0].get_attribute("href")
    else:
        next_page_link = None  # or you can set it to an empty string

    return table, links, next_page_link, tender_ids

def scrape_tender(driver, tender_ids, links, dict_tables_type, flag=None):
    """
    Scrape details for multiple tenders.
    
    :param driver: Selenium WebDriver instance
    :param tender_ids: List of tender IDs to scrape
    :param links: List of links to tender pages
    :param dict_tables_type: Dictionary mapping table names to their types
    :param flag: Flag to indicate if this is the first page (optional)
    """
    if flag == "first":
        links = links[:-1]
    else:
        links = links[:-2]

    for index, link in enumerate(links):
        try:
            driver.get(link)
            scrape_view_more_details(driver, tender_ids[index])
            scrape_view_stage_summary(driver, tender_ids[index], dict_tables_type)

            # Create directories if they don't exist
            os.makedirs("concatinated_csvs", exist_ok=True)
            os.makedirs("tenders_data", exist_ok=True)
            
            # Process in concatinated_csvs directory
            os.chdir("concatinated_csvs/")
            concatinate_csvs("../tenders_data/", "final_" + tender_ids[index])
            
            # Clean up temporary files
            directory = os.getcwd()
            remove_csvs(directory)
            os.chdir("../")
            directory = os.getcwd()
            remove_csvs(directory)
        except Exception as e:
            print(f"Error scraping tender {tender_ids[index]}: {str(e)}")

def run_scraper(driver=None, output_path=None, from_date=None, to_date=None, **kwargs):
    """
    Main function to run the scraper.
    
    :param driver: Selenium WebDriver instance (optional, will be created if not provided)
    :param output_path: Path to save output data (optional)
    :param from_date: Start date for scraping in format (year, month, day) (optional)
    :param to_date: End date for scraping in format (year, month, day) (optional)
    :param kwargs: Additional arguments
    :return: Dictionary with status and output path
    """
    # Set default URL
    url = 'https://etender.up.nic.in/nicgep/app?page=WebTenderStatusLists&service=page'
    
    # Create driver if not provided
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        # Set download preferences
        if output_path:
            prefs = {
                "download.default_directory": output_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(service=Service(), options=chrome_options)
    
    # Set output path
    if output_path:
        os.makedirs(output_path, exist_ok=True)
        os.chdir(output_path)
    
    # Create directories for scraped data
    os.makedirs("scraped_recent_tenders", exist_ok=True)
    os.chdir("scraped_recent_tenders")
    
    try:
        # Navigate to the URL
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        # Select tender status
        select_drop_down(driver, '//*[@id="tenderStatus"]', "6")  # Status code 6
        time.sleep(2)
        
        # Select date range if provided
        if from_date:
            # Parse from_date
            if isinstance(from_date, str):
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            
            # Click on from date field
            from_date_element = get_page_element(driver, '//*[@id="fromDate"]')
            from_date_element.click()
            
            # Select date from picker
            select_date_from_picker(
                driver, 
                picker_type="from", 
                year=str(from_date.year), 
                month_index=str(from_date.month - 1),  # Month index is 0-based
                day=from_date.day
            )
        
        if to_date:
            # Parse to_date
            if isinstance(to_date, str):
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            
            # Click on to date field
            to_date_element = get_page_element(driver, '//*[@id="toDate"]')
            to_date_element.click()
            
            # Select date from picker
            select_date_from_picker(
                driver, 
                picker_type="to", 
                year=str(to_date.year), 
                month_index=str(to_date.month - 1),  # Month index is 0-based
                day=to_date.day
            )
        
        # Handle CAPTCHA
        captcha_text = process_captcha(driver, '//*[@id="captchaImage"]', '//*[@id="captchaText"]')
        
        # Click search button
        search_button = get_page_element(driver, '//*[@id="Search"]')
        search_button.click()
        time.sleep(3)
        
        # Check if CAPTCHA validation failed and handle it
        captcha_success = check_captcha_and_reload(
            driver, 
            '//*[@id="captchaImage"]', 
            '//*[@id="captchaText"]',
            '//*[@id="Search"]'
        )
        
        if not captcha_success:
            print("CAPTCHA validation failed after multiple attempts.")
            return {"status": "error", "message": "CAPTCHA validation failed"}
        
        # Start scraping tenders
        tender_ids_list = []
        table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
        scrape_tender(driver, tender_ids, links, dict_tables_type, "first")
        
        # Scrape additional pages if available
        page_count = 1
        max_pages = 5  # Limit the number of pages to scrape
        
        while next_page_link is not None and page_count < max_pages:
            print(f"Moving to page {page_count + 1}")
            driver.get(next_page_link)
            table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
            scrape_tender(driver, tender_ids, links, dict_tables_type)
            page_count += 1
        
        print("Scraping completed successfully")
        return {"status": "success", "output_path": output_path or os.getcwd()}
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        # Don't close the driver if it was passed in
        if driver is not None and 'driver' not in kwargs:
            driver.quit()

# For testing the script directly
if __name__ == "__main__":
    run_scraper()
