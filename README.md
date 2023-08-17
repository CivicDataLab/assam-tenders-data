### About:
Fiscal ecosystem consist of hierarchial system through which flow of funds takes place. The most granuler level is tendering where government departments open bids for a project to be done like building of ramp for a school. Therefore to analyse and increase the effectiveness and transparency of this system we developed a [platform](assam.open-contracting.in/) (Assam Public Procurement Platform) for Assam (state of India). This platform aims at increasing transparency by storing all tenders at the same place. 
<br>
Assam government uploads contract data almost daily on [etenders platform]([url](https://assamtenders.gov.in/nicgep/app)https://assamtenders.gov.in/nicgep/app). The data publised in this platform is scattered and under captchas. Hence is becomes a bottleneck for users to analyse this data. To solve this we have scraped the data and stored it in a form which is much easier to use and understand. To make this happen we developed various scrapers and applied transformations on the mined data.

### Directory Structure:
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
### Steps followed:
- Data mining: read about how we scraped assam data [here](code/scraper/README.md)
- Transformation: there are multilevel transformations perform on the data before uploading to the platform, refer to [README.md](data/README.md)
### Frequecy of data upload:
We update the platform with new data in every 3 months
### Way Forward:
We are planning to scale this work to other states of India such as Himachal Pradesh, Odisa etc.
