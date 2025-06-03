from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os

# Import custom operator
try:
    from operators.web_scraper_operator import WebScraperOperator
except ImportError:
    from airflow.plugins.operators.web_scraper_operator import WebScraperOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'assam_tenders_scraper',
    default_args=default_args,
    description='Scrape Assam tenders data',
    schedule_interval=timedelta(days=1),  # Run daily
    start_date=days_ago(1),
    catchup=False,
    tags=['scraper', 'tenders', 'assam'],
)

# Define the base directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
output_dir = os.path.join(base_dir, 'data', 'scraped_data')
script_path = os.path.join(base_dir, 'airflow', 'include', 'assam_tenders_scraper.py')

# Create output directory task
create_output_dir = BashOperator(
    task_id='create_output_dir',
    bash_command=f'mkdir -p {output_dir}',
    dag=dag,
)

# Scrape tenders task using custom operator
scrape_tenders = WebScraperOperator(
    task_id='scrape_tenders',
    script_path=script_path,
    output_path=output_dir,
    headless=True,
    from_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # Last 30 days
    to_date=datetime.now().strftime('%Y-%m-%d'),  # Today
    dag=dag,
)

# Process data task (can be expanded as needed)
process_data = BashOperator(
    task_id='process_data',
    bash_command=f'echo "Processing data in {output_dir}"',
    dag=dag,
)

# Define task dependencies
create_output_dir >> scrape_tenders >> process_data
