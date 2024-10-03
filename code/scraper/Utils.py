import pandas as pd
from logging.config import fileConfig
import os
import re
from requests.adapters import HTTPAdapter
import csv
import glob
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
from urllib3.util import Retry
import time

MAX_RELOADS = 5
SLEEP_TIME = 30
class SeleniumScrappingUtils(object):
    def __init__(self):
        pass


    def sanitize_filename(filename):
        # Remove invalid characters and replace spaces with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = sanitized.replace(' ', '_')
        # Truncate filename if it's too long (Windows has a 255-character limit)
        return sanitized[:255]



    def get_tender_id(path):
        dataframe = pd.read_csv(path)
        tender_id = dataframe["tender.id"][dataframe['tender.stage'] == "AOC"]
        return tender_id
    
    def get_multiple_page_elements(driver,xpath = None):
        '''
        returns list of page element identifies with the given path
        '''
        page_element = WebDriverWait(driver, SLEEP_TIME).until(EC.presence_of_all_elements_located((By.XPATH,xpath)))
        return page_element
    
    def get_page_element(driver, xpath=None):
        ''' Get page element by xpath
        '''
        page_element = WebDriverWait(driver, SLEEP_TIME).until(EC.presence_of_element_located((By.XPATH,xpath)))
        return page_element
    def input_text_box(driver, select_element, text=None):
        '''
        Input text in input box
        '''
        select_element.send_keys(text)
    def save_image_as_png(image_element):
        '''
        Save a image from web to png helps in captcha breaking 
        '''
        with open('captcha_image.png', 'wb') as file:
             file.write(image_element.screenshot_as_png)
    def get_text_from_element(element):
        ''' Extracts name from webelement'''
        name_of_element = [element[i].text for i in range(len(element))]
        return name_of_element

    def extract_vertical_table(table_section, name_of_file, skip_header_number=None):
        '''
        Extracts vertical tables
        '''
        # Sanitize the filename
        safe_filename = SeleniumScrappingUtils.sanitize_filename(str(name_of_file))

        with open(safe_filename + ".csv", 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile)
            for row in table_section.find_elements(By.CSS_SELECTOR, 'tr')[skip_header_number:]:
                wr.writerow([d.text for d in row.find_elements(By.CSS_SELECTOR, 'td')])
    def extract_horizontal_table(table_section, name_of_file, skip_header_number=None):
        '''
        Extracts horizontal tables
        '''
        # Sanitize the filename
        safe_filename = SeleniumScrappingUtils.sanitize_filename(str(name_of_file))

        with open(safe_filename + ".csv", 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile)
            for row in table_section.find_elements(By.CSS_SELECTOR, "tbody"):
                wr.writerow(
                    [d.text for d in row.find_elements(By.CSS_SELECTOR, 'td:nth-of-type(2n+1)')[skip_header_number:]])
                wr.writerow([d.text for d in row.find_elements(By.CSS_SELECTOR, 'td:nth-of-type(2n+2)')])
                
    def concatinate_csvs(path_to_save,name_of_file):
        '''
        combines all the csvs
        '''
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ], axis = 1)
        combined_csv.to_csv(path_to_save + name_of_file+".csv", index=False, encoding='utf-8-sig')
   
    def remove_csvs(directory):
        '''
        removes all the csvs
        '''
        files_in_directory = os.listdir(directory)
        filtered_files = [file for file in files_in_directory if file.endswith(".csv")]
        for file in filtered_files:
            path_to_file = os.path.join(directory, file)
            os.remove(path_to_file)

    def is_file_downloaded(filename, timeout=500):
        end_time = time.time() + timeout
        while not glob.glob(filename):
            time.sleep(1)
            if time.time() > end_time:
                print("File not found within time")
                return False

        if glob.glob(filename):
            print("File found")
            return True
    
    def select_drop_down(driver,id,value):
         selected_element = Select(driver.find_element("xpath",id))
         selected_element.select_by_value(value)