import pandas as pd
import os
import re
import csv
import glob
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import shutil

MAX_RELOADS = 5
SLEEP_TIME = 30

def select_date_from_picker(driver, picker_type, year, month_index, day):
    """
    Select a date from the date picker in the web interface.
    
    :param driver: Selenium WebDriver instance
    :param picker_type: "from" or "to"
    :param year: Year to select (e.g., "2023")
    :param month_index: Month index (0 for January, 11 for December)
    :param day: Day of month (1-31)
    """
    try:
        # Determine which date picker we're working with
        picker_index = "2" if picker_type == "from" else "3"
        base_xpath = f'//*[@id="Body"]/div[{picker_index}]'
        
        # Wait for the date picker to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, base_xpath))
        )
        
        # Select month and year
        try:
            # Select month
            month_dropdown = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f'{base_xpath}/div[1]/table/tbody/tr/td[2]/select'))
            )
            select_drop_down(driver, f'{base_xpath}/div[1]/table/tbody/tr/td[2]/select', value=month_index)
            
            # Select year
            year_dropdown = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f'{base_xpath}/div[1]/table/tbody/tr/td[3]/select'))
            )
            select_drop_down(driver, f'{base_xpath}/div[1]/table/tbody/tr/td[3]/select', value=year)
            
            # Give the calendar time to update after changing month/year
            time.sleep(1)
        except Exception as e:
            print(f"Error selecting month/year: {str(e)}")
        
        # First try to find the exact day
        day_found = False
        try:
            # Look for the specific day
            for r in range(1, 7):  # rows
                if day_found:
                    break
                for c in range(1, 8):  # columns
                    try:
                        cell_xpath = f"{base_xpath}/div[2]/table/tbody/tr[{r}]/td[{c}]"
                        cell = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, cell_xpath))
                        )
                        
                        if cell.text.strip() == str(day):
                            # Check if the day is clickable (not disabled)
                            if 'disabled' not in cell.get_attribute('class'):
                                driver.execute_script("arguments[0].click();", cell)
                                day_found = True
                                print(f"Selected day {day} successfully")
                                return
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error finding specific day: {str(e)}")
        
        # If day not found or not clickable, select the middle day of the month
        if not day_found:
            print(f"Day {day} not found or not clickable in calendar. Selecting middle day of month.")
            try:
                # Find all available (non-disabled) days
                available_days = []
                for r in range(1, 7):  # rows
                    for c in range(1, 8):  # columns
                        try:
                            cell_xpath = f"{base_xpath}/div[2]/table/tbody/tr[{r}]/td[{c}]"
                            cell = driver.find_element(By.XPATH, cell_xpath)
                            
                            # Check if it's a valid day (has text and is not disabled)
                            if cell.text.strip() and 'disabled' not in cell.get_attribute('class'):
                                available_days.append((cell, int(cell.text.strip())))
                        except:
                            continue
                
                if available_days:
                    # Sort by day number
                    available_days.sort(key=lambda x: x[1])
                    
                    # Select the middle day of the available days
                    middle_index = len(available_days) // 2
                    middle_day = available_days[middle_index][0]
                    driver.execute_script("arguments[0].click();", middle_day)
                    print(f"Selected middle day {available_days[middle_index][1]} instead of {day}")
                    return
                else:
                    print("No available days found in the calendar")
            except Exception as e:
                print(f"Error selecting alternative day: {str(e)}")
            
            # Last resort: try to click on any visible day
            try:
                for r in range(1, 7):  # rows
                    for c in range(1, 8):  # columns
                        try:
                            cell = driver.find_element(By.XPATH, f"{base_xpath}/div[2]/table/tbody/tr[{r}]/td[{c}]")
                            if cell.text.strip():
                                driver.execute_script("arguments[0].click();", cell)
                                print(f"Selected day {cell.text.strip()} as last resort")
                                return
                        except:
                            continue
            except Exception as e:
                print(f"Error in last resort day selection: {str(e)}")
    
    except Exception as e:
        print(f"Error in date picker: {str(e)}. Skipping date selection.")
    finally:
        # If we get here, try to close the date picker by clicking outside
        try:
            driver.find_element(By.XPATH, '//*[@id="Body"]').click()
            print("Closed date picker by clicking outside")
        except:
            print("Failed to close date picker")
            pass

def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters and replacing spaces with underscores.
    
    :param filename: Original filename
    :return: Sanitized filename
    """
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    # Truncate filename if it's too long (Windows has a 255-character limit)
    return sanitized[:255]

def get_tender_id(path):
    """
    Extract tender ID from a CSV file.
    
    :param path: Path to the CSV file
    :return: Tender ID
    """
    dataframe = pd.read_csv(path)
    tender_id = dataframe["tender.id"][dataframe['tender.stage'] == "AOC"]
    return tender_id

def get_multiple_page_elements(driver, xpath=None):
    """
    Get multiple page elements by XPath.
    
    :param driver: Selenium WebDriver instance
    :param xpath: XPath to the elements
    :return: List of web elements
    """
    page_element = WebDriverWait(driver, SLEEP_TIME).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    return page_element

def get_page_element(driver, xpath=None):
    """
    Get a page element by XPath.
    
    :param driver: Selenium WebDriver instance
    :param xpath: XPath to the element
    :return: Web element
    """
    page_element = WebDriverWait(driver, SLEEP_TIME).until(EC.presence_of_element_located((By.XPATH, xpath)))
    return page_element

def input_text_box(driver, select_element, text=None):
    """
    Input text in an input box.
    
    :param driver: Selenium WebDriver instance
    :param select_element: Web element to input text into
    :param text: Text to input
    """
    select_element.send_keys(text)

def save_image_as_png(image_element):
    """
    Save an image from web to PNG (helps in captcha breaking).
    
    :param image_element: Web element containing the image
    """
    with open('captcha_image.png', 'wb') as file:
        file.write(image_element.screenshot_as_png)

def get_text_from_element(element):
    """
    Extract text from web elements.
    
    :param element: List of web elements
    :return: List of text from elements
    """
    name_of_element = [element[i].text for i in range(len(element))]
    return name_of_element

def extract_vertical_table(table_section, name_of_file, skip_header_number=None):
    """
    Extract data from a vertical table and save to CSV.
    
    :param table_section: Web element containing the table
    :param name_of_file: Name for the output file
    :param skip_header_number: Number of header rows to skip
    """
    # Sanitize the filename
    safe_filename = sanitize_filename(str(name_of_file))

    with open(safe_filename + ".csv", 'w', newline='', encoding='utf-8') as csvfile:
        wr = csv.writer(csvfile)
        for row in table_section.find_elements(By.CSS_SELECTOR, 'tr')[skip_header_number:]:
            wr.writerow([d.text for d in row.find_elements(By.CSS_SELECTOR, 'td')])

def extract_horizontal_table(table_section, name_of_file, skip_header_number=None):
    """
    Extract data from a horizontal table and save to CSV.
    
    :param table_section: Web element containing the table
    :param name_of_file: Name for the output file
    :param skip_header_number: Number of header rows to skip
    """
    # Sanitize the filename
    safe_filename = sanitize_filename(str(name_of_file))

    with open(safe_filename + ".csv", 'w', newline='', encoding='utf-8') as csvfile:
        wr = csv.writer(csvfile)
        for row in table_section.find_elements(By.CSS_SELECTOR, "tbody"):
            wr.writerow(
                [d.text for d in row.find_elements(By.CSS_SELECTOR, 'td:nth-of-type(2n+1)')[skip_header_number:]])
            wr.writerow([d.text for d in row.find_elements(By.CSS_SELECTOR, 'td:nth-of-type(2n+2)')])

def concatinate_csvs(path_to_save, name_of_file):
    """
    Combine all CSV files in the current directory.
    
    :param path_to_save: Path to save the combined CSV
    :param name_of_file: Name for the combined file
    """
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    if all_filenames:
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames], axis=1)
        os.makedirs(path_to_save, exist_ok=True)
        combined_csv.to_csv(path_to_save + name_of_file + ".csv", index=False, encoding='utf-8-sig')

def remove_csvs(directory):
    """
    Remove all CSV files in a directory.
    
    :param directory: Directory to clean up
    """
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".csv")]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)

def is_file_downloaded(filename, timeout=500):
    """
    Check if a file has been downloaded.
    
    :param filename: Name of the file to check
    :param timeout: Timeout in seconds
    :return: True if file exists, False otherwise
    """
    end_time = time.time() + timeout
    while not glob.glob(filename):
        time.sleep(1)
        if time.time() > end_time:
            print("File not found within time")
            return False

    if glob.glob(filename):
        print("File found")
        return True

def select_drop_down(driver, id, value):
    """
    Select an option from a dropdown menu.
    
    :param driver: Selenium WebDriver instance
    :param id: XPath to the dropdown element
    :param value: Value to select
    """
    selected_element = Select(driver.find_element(By.XPATH, id))
    selected_element.select_by_value(value)
