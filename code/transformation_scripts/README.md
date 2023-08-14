This script converts scraped raw data into [Open Contracting Data Standards](https://standard.open-contracting.org/latest/en/). 

### How to run the script:
* `git clone https://github.com/CivicDataLab/assam-tender-data.git`
* `pip3 install virtualenv`
* `python3 -m venv /path/to/virtual/env`
* `virtualenv /path/to/virtual/env/source/bin/activate`
* `cd assam-tender-data/code/transformation_scripts`
* `pip3 -r install requirements.txt`
* Before running the script:
  > change path of the raw data in the script
* `python3 data_prep_ocds_mapping.py`

### Contributions:
* [@sphanidatta](https://github.com/orgs/CivicDataLab/people/sphanidatta)