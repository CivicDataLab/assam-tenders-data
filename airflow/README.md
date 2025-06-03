# Airflow Scraper Setup for Assam Tenders Data

## Overview

This directory contains the Airflow setup for automating the scraping and processing of Assam tenders data. The scrapers have been migrated from standalone scripts to Airflow DAGs (Directed Acyclic Graphs) to enable scheduling, monitoring, and better error handling.

## Directory Structure

```
airflow/
├── config/           # Airflow configuration files
├── dags/             # Airflow DAG definitions
│   ├── assam_tenders_scraper_dag.py       # Basic scraper DAG
│   ├── assam_tenders_etl_dag.py           # ETL pipeline DAG
│   └── data_maintenance_dag.py            # Maintenance tasks DAG
├── include/          # Shared code and utilities
│   ├── assam_tenders_scraper.py           # Main scraper code
│   ├── captcha_utils.py                   # CAPTCHA handling utilities
│   └── scraper_utils.py                   # General scraper utilities
├── logs/             # Airflow logs
└── plugins/          # Custom Airflow plugins
    └── operators/    # Custom operators
        ├── __init__.py
        └── web_scraper_operator.py        # Custom operator for web scraping
```

## Available DAGs

1. **assam_tenders_scraper_dag**: A basic DAG that runs the scraper daily to collect tender data.
2. **assam_tenders_etl_dag**: A more comprehensive ETL pipeline that scrapes, processes, and transforms the data.
3. **data_maintenance_dag**: A maintenance DAG that runs weekly to archive old data and perform quality checks.

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the setup script to initialize the Airflow environment:
   ```
   bash setup_airflow.sh
   ```

3. Access the Airflow UI at http://localhost:8080 (default username: admin, password: admin)

4. Enable the DAGs in the Airflow UI to start the automated scraping.

## Customizing the Scrapers

### Modifying Scraping Parameters

You can customize the scraping parameters by editing the DAG files in the `dags/` directory. For example, to change the date range for scraping, modify the `from_date` and `to_date` parameters in the `WebScraperOperator` task.

### Adding New Scrapers

To add a new scraper:

1. Create a new scraper script in the `include/` directory
2. Create a new DAG file in the `dags/` directory
3. Use the `WebScraperOperator` to run your scraper

## Troubleshooting

### Common Issues

1. **CAPTCHA Handling**: If the scraper is failing due to CAPTCHA issues, you may need to adjust the CAPTCHA handling parameters in `captcha_utils.py`.

2. **WebDriver Issues**: If you encounter WebDriver errors, make sure you have the correct version of ChromeDriver installed. The scraper uses webdriver-manager to handle this automatically, but you may need to update your Chrome browser.

3. **Permission Issues**: If you encounter permission issues when running the scrapers, make sure the output directories have the correct permissions.

### Logs

Check the Airflow logs for detailed error messages and debugging information. Logs are stored in the `logs/` directory.

## Data Storage

The scraped data is stored in the following directories:

- **Raw Data**: `data/raw/`
- **Processed Data**: `data/processed/`
- **Final Data**: `data/final/`
- **Archived Data**: `data/archive/`

## Maintenance

The `data_maintenance_dag` performs the following tasks:

1. Archives data files older than 30 days
2. Checks disk usage and logs warnings if usage is high
3. Performs data quality checks on the final data

You can customize the maintenance tasks by editing the `data_maintenance_dag.py` file.
