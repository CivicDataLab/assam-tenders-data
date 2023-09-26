[![image](https://github.com/CivicDataLab/assam-tender-data/assets/5118689/f7d654c8-d077-4d03-a616-7e7b682c1fc5)](https://assam.open-contracting.in/)

### About
The fiscal ecosystem operates as a hierarchical system facilitating the flow of funds. At its most granular level, the process involves tendering, where government departments solicit bids for various projects, such as constructing a ramp for a school. In our efforts to enhance the efficiency and transparency of this system, we have created the [Assam Public Procurement Platform](assam.open-contracting.in/), specifically for the state of Assam in India. This platform is designed to promote transparency by consolidating all tender information in one central location.

The Assam government regularly uploads contract data on the [etenders platform](https://assamtenders.gov.in/nicgep/app), with new data added almost daily. Unfortunately, the data on this platform is fragmented and often protected by captchas, creating significant hurdles for users attempting to analyze it effectively. To address this issue, we have employed web scraping techniques to collect and organize the data in a user-friendly and comprehensible format. This involved developing multiple scrapers and implementing various data transformations to achieve our goal.

### Directory Structure
- [LICENSE](LICENSE)
- [README.md](README.md)
- code
  - scraper
    - [README.md](code/scraper/README.md)
    - [Utils.py](code/scraper/Utils.py)
    - [WebDriver.py](code/scraper/WebDriver.py)
    - [requirements.txt](code/scraper/requirements.txt)
    - [scraper_assam_recent_tenders_tender_status.py](code/scraper/scraper_assam_recent_tenders_tender_status.py)
  - transformation_scripts
    - [README.md](code/transformation_scripts/README.md)
    - [data_prep_ocds_mapping.py](code/transformation_scripts/data_prep_ocds_mapping.py)
    - [requirements.txt](code/transformation_scripts/requirements.txt)
- data
  - ProcessedData
    - ocds-mapped-data
      - [ocds_mapped_data_fiscal_year_2016_2020_v1.json](data/ProcessedData/ocds-mapped-data/ocds_mapped_data_fiscal_year_2016_2020_v1.json)
      - [ocds_mapped_data_fiscal_year_2016_2020_v1.xlsx](data/ProcessedData/ocds-mapped-data/ocds_mapped_data_fiscal_year_2016_2020_v1.xlsx)
      - [ocds_mapped_data_fiscal_year_2016_2022_v2.csv](data/ProcessedData/ocds-mapped-data/ocds_mapped_data_fiscal_year_2016_2022_v2.csv)
      - [ocds_mapped_data_fiscal_year_2016_2022_v2.json](data/ProcessedData/ocds-mapped-data/ocds_mapped_data_fiscal_year_2016_2022_v2.json)
  - [README.md](data/README.md)
  - RawData
    - [raw_data_fy_2016_2022.zip](data/RawData/raw_data_fy_2016_2022.zip)

### Process
- [Data mining](code/scraper/README.md)
- [Data Transformations](data/README.md)

### Data Update Frequecy
We update the platform with new data in every 3 months

### License
All scripts are published under the [GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html#SEC1) license and all datasets are published under the [Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/summary/).
