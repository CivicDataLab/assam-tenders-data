#!/usr/bin/env python3
"""
Standalone script to run the Assam tenders scraper.
This script is designed to be run directly from a bash command in Airflow.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the current directory to the path so we can import the scraper modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the scraper module
from assam_tenders_scraper import run_scraper



def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the Assam tenders scraper')
    parser.add_argument('--output-path', type=str, required=True, help='Path to save the scraped data')
    parser.add_argument('--from-date', type=str, help='Start date for scraping (YYYY-MM-DD)')
    parser.add_argument('--to-date', type=str, help='End date for scraping (YYYY-MM-DD)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()
    
    # Set up Chrome options
    options = Options()
    if args.headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    
    # Set up unhandled prompt behavior
    options.set_capability('unhandledPromptBehavior', 'accept')
    
    # Set up download preferences
    prefs = {
        "download.default_directory": args.output_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Set default dates if not provided
    if not args.from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        from_date = args.from_date
        
    if not args.to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    else:
        to_date = args.to_date
    
    # Create the output directory
    os.makedirs(args.output_path, exist_ok=True)
    
    # Connect to the remote Selenium service
    print(f"Connecting to Selenium service...")
    driver = None
    scraping_success = False
    
    try:
        driver = webdriver.Remote(
            command_executor='http://selenium-chrome:4444/wd/hub',
            options=options
        )
        
        # Run the scraper
        print(f"Starting scraper with dates: {from_date} to {to_date}")
        result = run_scraper(
            driver=driver,
            output_path=args.output_path,
            from_date=from_date,
            to_date=to_date
        )
        
        print(f"Scraper completed with result: {result}")
        
        # Check if the scraper was successful
        if result.get('status') == 'error':
            print(f"Scraper failed: {result.get('message')}")
            scraping_success = False
        else:
            # Check if any files were created
            files = os.listdir(args.output_path)
            csv_files = [f for f in files if f.endswith('.csv')]
            
            if not csv_files:
                print("No CSV files were created in the output directory.")
                scraping_success = False
            else:
                print(f"Successfully scraped data. Files created: {csv_files}")
                scraping_success = True
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        scraping_success = False
    finally:
        # Close the driver
        if driver:
            try:
                # Try to dismiss any alerts
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print(f"Alert found: {alert_text}")
                    alert.accept()
                except Exception:
                    pass
                
                # Quit the driver
                driver.quit()
                print("WebDriver closed successfully")
            except Exception as e:
                print(f"Error closing WebDriver: {str(e)}")
    
    # Return appropriate exit code based on scraping success
    return 0 if scraping_success else 1

if __name__ == "__main__":
    sys.exit(main())
