# This file determines the setting of webdriver for the scraper
from selenium import webdriver 

class WebDriver(object):

    def __init__(self,path):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option("prefs", {
          # "download.default_directory": r"/Users/shreyaagrawal/Documents/Cdl/assam-tender-scraper/scraped_live_tender_data",
          "download.default_directory": r"/home/bhavabhuthi/Documents/CDL/assam-tenders-data/scraped_recent_tenders",
          "download.prompt_for_download": False,
          "download.directory_upgrade": True,
          "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(executable_path = path, chrome_options = chrome_options)
        
        
        