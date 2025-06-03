from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class WebScraperOperator(BaseOperator):
    """
    Operator for web scraping using Selenium.
    
    :param script_path: Path to the scraper script
    :param script_args: Arguments to pass to the scraper script
    :param output_path: Path to store the output data
    :param chrome_options: Additional Chrome options
    :param headless: Whether to run Chrome in headless mode
    :param from_date: Start date for scraping (optional)
    :param to_date: End date for scraping (optional)
    """
    
    @apply_defaults
    def __init__(
        self,
        script_path,
        output_path,
        script_args=None,
        chrome_options=None,
        headless=True,
        from_date=None,
        to_date=None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.script_path = script_path
        self.script_args = script_args or {}
        self.output_path = output_path
        self.chrome_options = chrome_options or []
        self.headless = headless
        self.from_date = from_date
        self.to_date = to_date
        
    def execute(self, context):
        """
        Execute the web scraping operation.
        """
        self.log.info(f"Starting web scraping operation with script: {self.script_path}")
        
        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
        
        # Set up Chrome options
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        
        # Add custom Chrome options
        for option in self.chrome_options:
            options.add_argument(option)
            
        # Set download preferences
        prefs = {
            "download.default_directory": self.output_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # Add capabilities to handle alerts
        options.set_capability('unhandledPromptBehavior', 'accept')
        
        driver = None
        result = {"status": "success", "message": "Task completed", "output_path": self.output_path}
        
        try:
            # Connect to the remote Selenium service
            driver = webdriver.Remote(
                command_executor='http://selenium-chrome:4444/wd/hub',
                options=options
            )
            
            # Import and run the scraper script
            import importlib.util
            import sys
            
            # Add script directory to path
            script_dir = os.path.dirname(self.script_path)
            if script_dir not in sys.path:
                sys.path.append(script_dir)
            
            # Load the script as a module
            spec = importlib.util.spec_from_file_location(
                "scraper_module", self.script_path
            )
            scraper_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scraper_module)
            
            # Set up context for the scraper
            scraper_context = {
                "driver": driver,
                "output_path": self.output_path,
                "from_date": self.from_date,
                "to_date": self.to_date,
                **self.script_args
            }
            
            # Run the scraper's main function if it exists
            if hasattr(scraper_module, "run_scraper"):
                try:
                    scraper_result = scraper_module.run_scraper(**scraper_context)
                    self.log.info("Web scraping completed successfully")
                    if isinstance(scraper_result, dict):
                        result.update(scraper_result)
                except Exception as e:
                    self.log.error(f"Error in scraper: {str(e)}")
                    result["status"] = "partial_success"
                    result["error"] = str(e)
            else:
                self.log.warning("No 'run_scraper' function found in the script. The script might not be compatible with this operator.")
                result["status"] = "warning"
                result["message"] = "No run_scraper function found"
                
        except Exception as e:
            self.log.error(f"Error during web scraping setup: {str(e)}")
            result["status"] = "error"
            result["message"] = str(e)
        
        # Close the driver in a separate try-except block
        if driver is not None:
            try:
                # First try to dismiss any alerts that might be present
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    self.log.info(f"Alert found: {alert_text}")
                    alert.accept()
                except Exception:
                    # No alert present, continue
                    pass
                    
                # Now try to close the driver
                driver.quit()
            except Exception as e:
                self.log.warning(f"Error closing WebDriver: {str(e)}")
                # Don't let driver errors fail the task
        
        # Always return a result, never raise an exception
        return result

