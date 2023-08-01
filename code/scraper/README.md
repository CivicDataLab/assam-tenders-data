### Assam procurement data:
Procurement data holds information on the process of collecting, organizing, and managing all information related to the acquisition of goods or services from external sources.
Governement of Assam uploads this information on etenders platform, in form of `html` tables.
Our goal is to collect this information present under the layers of captcha and present it in
machine readable, research friendly manner.
### Data Source:
[Assam etenders website](https://assamtenders.gov.in/nicgep/app) has various sections through which different information can be gathered. After doing scoping excercise we are scraping data from [`Tender Status`](https://assamtenders.gov.in/nicgep/app?page=WebTenderStatusLists&service=page) section
### What does each script do:
- `WebDriver.py` : Configures selenium webdriver
- `Utils.py` : Has multiple utility functions which are re-used in different projects
- `scraper_assam_recent_tenders_tender_status.py` : Runs the logic of minning data from the portal with the help of above two modules
### Setup instructions for scraper:
- `git clone https://github.com/CivicDataLab/assam-tender-data.git`
- `pip3 install virtualenv`
- `python3 -m venv /path/to/virtual/env`
- `virtualenv /path/to/virtual/env/source/bin/activate`
- `cd assam-tender-data/code/scraper`
- `mkdir scraped_recent_tenders`
- `cd scraped_recent_tenders`
- `mkdir concatinated_csvs`
- `cd ../`
- `pip3 -r install requirements.txt`
- Before running the script make sure to change following paramenters:
    >  Configure path of chromedriver in `WebDriver.py`
    >  Configure range of date in `scraper_assam_recent_tenders_tender_status.py`
- `python3 scraper_assam_recent_tenders_tender_status.py`
### Link and metadata of scraped data:
```
Time range: Fiscal year 2016-2017 to fiscal year 2022-2023
Last updated: 2023-06-21
Frequency of update: Quarterly
Link:
```
### Contributions:
. [@sphanidatta](https://github.com/orgs/CivicDataLab/people/sphanidatta)

### License:
