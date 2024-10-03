from selenium.webdriver.support.wait import WebDriverWait

from WebDriver import WebDriver
from Utils import SeleniumScrappingUtils
import time
import os
import warnings
from captcha import captcha

import pdb
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

warnings.filterwarnings("ignore", category=DeprecationWarning)
url = 'https://assamtenders.gov.in/nicgep/app?page=WebTenderStatusLists&service=page'
# browser = WebDriver("/home/bhavabhuthi/Downloads/chrome-linux64/chrome-linux64/chrome")
chromedriver_path = ""

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

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



def captcha_input(xpath_image, xpath_input_text):
    captcha_text = captcha(driver, xpath_image)
    captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
    time.sleep(3)
    SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)
    invalid_string = driver.find_elements(By.CLASS_NAME, "error")

    # Click the search button
    search_button = SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Search"]')
    search_button.click()
    #check_captcha_and_reload(driver, xpath_image, xpath_input_text)


    while len(invalid_string) != 0:
        pdb.set_trace()
        captcha_text = captcha(driver, xpath_image)
        captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
        SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)
        time.sleep(3)
        invalid_string = driver.find_elements(By.CLASS_NAME, "error")
        print("CAPTCHA validation failed. Reloading CAPTCHA...")

        # # Reload CAPTCHA image
        # reload_button = driver.find_element(By.XPATH,
        #                                     "/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr[19]/td/table/tbody/tr/td[3]/button")
        # reload_button.click()
        # time.sleep(2)  # Give some time for the new CAPTCHA to load
        #
        # # Solve the new CAPTCHA
        # captcha_text = captcha(driver, xpath_image)  # Solve the new CAPTCHA using the same xpath_image
        # captcha_input_element = SeleniumScrappingUtils.get_page_element(driver, xpath_input_text)
        # SeleniumScrappingUtils.input_text_box(driver, captcha_input_element, captcha_text)
        #
        # time.sleep(3)  # Wait for the error message to be displayed again if CAPTCHA is wrong
        # invalid_string = driver.find_elements(By.CLASS_NAME, "error")  # Re-check for error

        if len(invalid_string) == 0:
            break


# Select tender status

SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="tenderStatus"]', "6")  # 3

# Select date for tender scraping;
# from date
from_date_element = SeleniumScrappingUtils.get_page_element(driver,
                                                            '//*[@id="frmSearchFilter"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/a')
from_date_element.click()
# Select month
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[2]/div[1]/table/tbody/tr/td[2]/select', value="3")
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
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[3]/div[1]/table/tbody/tr/td[2]/select', value="3")
# Select year
SeleniumScrappingUtils.select_drop_down(driver, '//*[@id="Body"]/div[3]/div[1]/table/tbody/tr/td[3]/select',
                                        value="2024")
# Select Date
SeleniumScrappingUtils.get_page_element(driver, '//*[@id="Body"]/div[3]/div[2]/table/tbody/tr[5]/td[3]').click()
# break captcha
captcha_input('//*[@id="captchaImage"]', '//*[@id="captchaText"]')


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
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "table_list")))

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
            print(f"Processing section {index}: {header_name}")

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
    tender_ids_list = []
    try:
        table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
        scrapeTender(driver, tender_ids, links, dict_tables_type, "first")
        while next_page_link is not None:
            print("Moving to next page")
            driver.get(next_page_link)
            table, links, next_page_link, tender_ids = get_table_links(driver, '//*[@id="tabList"]')
            scrapeTender(driver, tender_ids, links, dict_tables_type)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Scraping completed")
        driver.quit()
