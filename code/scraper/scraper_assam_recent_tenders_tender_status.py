from selenium.webdriver.support.wait import WebDriverWait
import time
from WebDriver import WebDriver
from Utils import SeleniumScrappingUtils
import time
import os
import warnings
from captcha import captcha, recaptcha
import json
from urllib.parse import urlparse, parse_qs
import pdb

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

warnings.filterwarnings("ignore", category=DeprecationWarning)
url = 'https://etender.up.nic.in/nicgep/app?page=WebTenderStatusLists&service=page'
# browser = WebDriver("/home/bhavabhuthi/Downloads/chrome-linux64/chrome-linux64/chrome")
chromedriver_path = ""

chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument("--start-maximized")
# Set up the Chrome service
chrome_service = Service(chromedriver_path)

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Open a webpage
driver.get(url)

# driver.get(url)

os.chdir("scraped_recent_tenders")
dict_tables_type = {"Bids List": "Vertical", "Technical Bid Opening Summary": "Horizontal",
                    "Technical Evaluation Summary Details": "Horizontal",
                    "Bid Opening Summary": "Horizontal",
                    "Finance Bid Opening Summary": "Horizontal",
                    "Financial Evaluation Bid List": "Vertical",
                    "Finance Evaluation Summary Details": "Horizontal",
                    "AOC": "Horizontal",
                    "Awarded Bids List": "Vertical",
                    "Tender Revocation List": "Vertical",
                    "Corrigendum Details": "Vertical"}

def check_captcha_and_reload(driver, xpath_image, xpath_input_text):
    while True:
        # Check if there is an error indicating CAPTCHA failure
        invalid_string = driver.find_elements(By.CLASS_NAME, "error")


        if len(invalid_string) == 0:
            break  # If no error, CAPTCHA is valid, break the loop

        print("CAPTCHA validation failed. Reloading CAPTCHA...")

        # Reload CAPTCHA image
        reload_button_xpath = "/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr[19]/td/table/tbody/tr/td[3]/button"
        reload_button = driver.find_element(By.XPATH, reload_button_xpath)
        reload_button.click()
        time.sleep(2)  # Wait for the CAPTCHA to reload

        # Solve the new CAPTCHA
        captcha_text = captcha(driver, xpath_image)
        captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
        SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)

        time.sleep(3)  # Wait for potential error message to reappear


def captcha_input(driver, xpath_image, xpath_input_text):
    def handle_invalid_captcha():
        print("\nCAPTCHA validation failed. Please re-enter the correct CAPTCHA.")

        # Prompt user for new input
        captcha_text = input("Enter the correct CAPTCHA text: ")

        # Clear and enter new captcha
        captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
        captcha_input_element.clear()
        SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)

        # Click search button
        search_button = SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Search"]')
        search_button.click()
        time.sleep(3)

        return driver.find_elements(By.XPATH, '//*[@id="If_19"]/table/tbody/tr/td/span/b')

    # Display the CAPTCHA image for user reference
    captcha_element = driver.find_element(By.XPATH, xpath_image)
    SeleniumScrappingUtils.save_image_as_png(captcha_element)
    print("\nCAPTCHA saved as 'captcha_image.png'. Please check the image and enter the text.")

    # Prompt user for initial CAPTCHA input
    captcha_text = input("Enter CAPTCHA text: ")

    # Enter user-provided CAPTCHA
    captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
    SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)

    # Click search button
    search_button = SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Search"]')
    search_button.click()
    time.sleep(3)

    # Validate CAPTCHA and retry if incorrect
    invalid_string = driver.find_elements(By.XPATH, '//*[@id="If_19"]/table/tbody/tr/td/span/b')
    while len(invalid_string) != 0:
        invalid_string = handle_invalid_captcha()

    return True

# Select tender status

time.sleep(10)

SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="tenderStatus"]', "6")  # 3



# Select date for tender scraping;
# from date
from_date_element = SeleniumScrappingUtils.get_page_element(driver,
                                                            '//*[@id="frmSearchFilter"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/a')
from_date_element.click()
# Select month
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[2]/div[1]/table/tbody/tr/td[2]/select', value="0")
# Select year
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[2]/div[1]/table/tbody/tr/td[3]/select',
                                        value="2024")
# Select Date
SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Body"]/div[2]/div[2]/table/tbody/tr[1]/td[2]').click()

# to_date
to_date_element = SeleniumScrappingUtils.get_page_element(driver,
                                                          '//*[@id="frmSearchFilter"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr[3]/td[4]/a')
to_date_element.click()
# Select month
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[3]/div[1]/table/tbody/tr/td[2]/select', value="1")
# Select year
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[3]/div[1]/table/tbody/tr/td[3]/select',
                                        value="2024")
# Select Date
SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Body"]/div[3]/div[2]/table/tbody/tr[5]/td[5]').click()
# break captcha

# Where you previously called captcha_input:
captcha_input(driver, '//*[@id="captchaImage"]', '//*[@id="captchaText"]')

def extract_sp_tokens_paginated(driver, dict_tables_type, output_file=r"C:\Users\cdl\Desktop\Scrapper\assam-tenders-data\code\scraper\scraped_recent_tenders\sp_tokens.json"):
    page_count = 1
    all_data = {}

    while True:
        with open(r"C:\Users\cdl\Desktop\Scrapper\assam-tenders-data\code\scraper\scraped_recent_tenders\cookies.json", "w") as f:
            json.dump(driver.get_cookies(), f)
        print(f"Processing page {page_count}...")
        table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
        page_key = f"page_{page_count}"
        page_dict = {}

        for tender_id, link in zip(tender_ids, links):
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            sp_token = query_params.get("sp", [""])[0]  # default to "" if missing
            page_dict[tender_id] = sp_token

        all_data[page_key] = page_dict

        # Move to next page if exists
        if next_page_link:
            driver.get(next_page_link)
            page_count += 1
        else:
            break

    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2)

    print(f"Saved all SP tokens to '{output_file}'")
                               

def scrape_view_more_details(driver, tender_id):
    view_more_details_element = SeleniumScrappingUtils.get_page_element(driver, '//*[@id="DirectLink"]')
    view_more_details_element.click()
    # since we are opening the new window selenium needs to change the focus
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)

    # all the table elements
    tables = SeleniumScrappingUtils.get_multiple_page_elements(driver,
                                                               '/html/body/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr[1]/td/table')[
        0].find_elements(By.CSS_SELECTOR, "table")              #/html/body/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr[1]/td/table
    dict_table_section_head = {}                                #html/body/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr/td/table
    for table_section_elements in tables:
        try:
            dict_table_section_head[
                table_section_elements.find_element(By.CLASS_NAME, "section_head").text] = table_section_elements
        except:
            continue
    for index, (keys, values) in enumerate(dict_table_section_head.items()):
        keys = keys.replace("/", "")
        if keys == "Tender Documents":
            continue
        # elif keys == "Work /Item(s)":
        #     SeleniumScrappingUtils.extract_horizontal_table(values,tender_id +"_"+"Work_Item"+"_" + str(index),1)
        elif (keys.startswith("Cover Details") or keys == "Latest Corrigendum List" or keys.startswith("Other")):
            SeleniumScrappingUtils.extract_vertical_table(values, tender_id + "_" + keys + "_" + str(index), 1)
        elif keys == "Payment Instruments":
            table_section = values.find_element(By.CSS_SELECTOR, "table")
            SeleniumScrappingUtils.extract_vertical_table(table_section, tender_id + "_" + keys + "_" + str(index), 1)
        else:
            SeleniumScrappingUtils.extract_horizontal_table(values, tender_id + "_" + keys + "_" + str(index), 1)
    path_to_save = "concatinated_csvs/"
    SeleniumScrappingUtils.concatinate_csvs(path_to_save, tender_id)
    directory = os.getcwd()
    #SeleniumScrappingUtils.remove_csvs(directory)
    window_after = driver.window_handles[0]
    driver.switch_to.window(window_after)


def scrape_view_stage_summary(driver, tender_id, dict_tables_type):

    list_of_dict_tables_type = list(dict_tables_type.keys())

    # Click on the summary link
    SeleniumScrappingUtils.get_page_element(driver, '//*[@id="DirectLink_0"]').click()

    # Switch to the new window
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)

    # Wait for the table elements to load
    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "table_list")))

    # Retrieve all relevant section elements
    sections = driver.find_elements(By.CLASS_NAME, "table_list")

    # Add additional elements if they exist
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
            header_name = section.find_element(By.CLASS_NAME, "section_head").text \
                if section.find_elements(
                By.CLASS_NAME, "section_head") \
                else "Unknown Section"

            # Print debug information
            #print(f"Processing section {index}: {header_name}")

            # Process table data based on header name
            if header_name in list_of_dict_tables_type:
                if dict_tables_type[header_name] == "Vertical":
                    SeleniumScrappingUtils.extract_vertical_table(section, header_name + "_" + tender_id, 1)
                else:
                    SeleniumScrappingUtils.extract_horizontal_table(section, header_name + "_" + tender_id, 1)
            else:
                # Default action for sections not in dict_tables_type
                SeleniumScrappingUtils.extract_horizontal_table(section, header_name + "_" + tender_id, 1)
        except Exception as e:
            print(f"Error processing section {index}: {e}")

    path_to_save = "concatinated_csvs/"
    SeleniumScrappingUtils.concatinate_csvs(path_to_save, "summary" + "_" + tender_id)
    # Switch back to the original window
    driver.switch_to.window(driver.window_handles[0])


def get_table_links(driver, table_xpath):
    table = SeleniumScrappingUtils.get_page_element(driver, table_xpath)
    elements_list = table.find_elements(By.CSS_SELECTOR, "a")
    links = [element.get_attribute("href") for element in elements_list]
    rows = table.find_elements(By.CSS_SELECTOR, "tr")
    tender_ids = [row.find_element("xpath", "td[2]").text for row in rows[1:-2]]

    # Check if the "loadNext" button exists before trying to access it
    next_page_elements = table.find_elements("xpath", '//*[@id="loadNext"]')
    if next_page_elements:
        next_page_link = next_page_elements[0].get_attribute("href")
    else:
        next_page_link = None  # or you can set it to an empty string

    return table, links, next_page_link, tender_ids


def scrapeTender(driver, tender_ids, links, dict_tables_type, flag=None, ):
    if flag == "first":
        links = links[:-1]
    else:
        links = links[:-2]

    for index, link in enumerate(links):
        driver.get(link)
        scrape_view_more_details(driver, tender_ids[index])
        scrape_view_stage_summary(driver, tender_ids[index], dict_tables_type)

        os.chdir("concatinated_csvs/")
        SeleniumScrappingUtils.concatinate_csvs("../tenders_data/", "final_" + tender_ids[index])
        directory = os.getcwd()
        SeleniumScrappingUtils.remove_csvs(directory)
        os.chdir("../")
        directory = os.getcwd()
        SeleniumScrappingUtils.remove_csvs(directory)
    # SeleniumScrappingUtils.get_page_element(driver,'//*[@id="PageLink_20"]').click()


if __name__ == "__main__":
    try:
        extract_sp_tokens_paginated(driver, dict_tables_type)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Token extraction completed")
        driver.quit()

# if __name__ == "__main__":
#     tender_ids_list = []
#     try:
#         table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')

#         # Add this to print the links on the first page
#         print("\nTender links on the first page:")
#         for tender_id, link in zip(tender_ids, links):
#             print(f"{tender_id}: {link}")
#         while next_page_link is not None:
#             print("Moving to next page")
#             driver.get(next_page_link)
#             table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
#             scrapeTender(driver, tender_ids, links, dict_tables_type)
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#     finally:
#         print("Scraping completed")
#         driver.quit()
