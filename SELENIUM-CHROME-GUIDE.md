# Using Selenium Standalone Chrome Container with Airflow

This guide explains how to use the Selenium standalone Chrome container that's integrated with your Airflow setup on Apple Silicon Mac.

## Overview

The Selenium standalone Chrome container provides:
- Pre-installed Chromium browser (ARM64-compatible)
- ChromeDriver that matches the Chromium version
- VNC server for debugging (accessible on port 7900)
- Selenium Grid interface (accessible on port 4444)

## Connecting to Selenium Chrome from Airflow

In your Python code, use the following pattern to connect to the Selenium Chrome container:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_chrome_driver():
    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Add headless mode if you don't need to see the browser
    # chrome_options.add_argument("--headless")
    
    # Connect to the Selenium standalone Chrome container
    driver = webdriver.Remote(
        command_executor='http://selenium-chrome:4444/wd/hub',
        options=chrome_options
    )
    return driver

# Example usage
driver = get_chrome_driver()
driver.get("https://example.com")
print(driver.title)
driver.quit()
```

## Watching Browser Activity (Debugging)

You can watch Chrome in action to debug your scraping code:

1. Access the VNC viewer at http://localhost:7900
2. Enter the password: `secret`
3. You'll see the Chrome browser running your automated tasks

## Testing Selenium Connection

Run the included test script to verify the connection is working:

```bash
docker compose exec airflow-webserver python /opt/airflow/scripts/selenium_test.py
```

## Modifying Your Existing Scraper Code

To adapt your existing scraping code to use the standalone Chrome container:

1. Replace any direct Chrome instances with the Remote WebDriver:
   ```python
   # Replace this:
   from selenium.webdriver.chrome.service import Service
   from webdriver_manager.chrome import ChromeDriverManager
   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
   
   # With this:
   driver = webdriver.Remote(
       command_executor='http://selenium-chrome:4444/wd/hub',
       options=chrome_options
   )
   ```

2. Update the `assam_tenders_scraper.py` file's `run_scraper` function:
   ```python
   def run_scraper(driver=None, output_path=None, from_date=None, to_date=None, **kwargs):
       # ... existing code ...
       
       # Create driver if not provided
       if driver is None:
           chrome_options = Options()
           chrome_options.add_argument("--no-sandbox")
           chrome_options.add_argument("--disable-dev-shm-usage")
           
           # Connect to Selenium standalone Chrome container
           driver = webdriver.Remote(
               command_executor='http://selenium-chrome:4444/wd/hub',
               options=chrome_options
           )
       
       # ... rest of function ...
   ```

## Benefits of This Approach

1. **Reliability**: The standalone container ensures Chrome is properly installed and configured
2. **Visual debugging**: You can see what's happening in the browser using the VNC interface
3. **Separation of concerns**: Web browser complexity is isolated in its own container
4. **Resource efficiency**: Chrome runs in a dedicated container with optimized resources

## Troubleshooting

If you encounter issues with the Selenium Chrome container:

1. Check if the container is running:
   ```bash
   docker compose ps selenium-chrome
   ```

2. View the container logs:
   ```bash
   docker compose logs selenium-chrome
   ```

3. Try increasing shared memory if you see crashes:
   ```yaml
   # In docker-compose.yml
   selenium-chrome:
     shm_size: 4g  # Increase as needed
   ```

4. Test connectivity from the Airflow webserver:
   ```bash
   docker compose exec airflow-webserver curl -I http://selenium-chrome:4444
   ```

5. Restart the container if needed:
   ```bash
   docker compose restart selenium-chrome
   ```

6. If you're having issues with the VNC viewer, try accessing it at:
   - http://localhost:7900
   - http://127.0.0.1:7900
   
   Password: `secret`