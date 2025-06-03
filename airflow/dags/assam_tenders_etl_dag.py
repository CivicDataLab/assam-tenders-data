from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.sensors.filesystem import FileSensor
import os
import sys
import pandas as pd

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
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'assam_tenders_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for Assam tenders data',
    schedule_interval='0 0 * * *',  # Run at midnight every day
    start_date=days_ago(1),
    catchup=False,
    tags=['scraper', 'tenders', 'assam', 'etl'],
)

# Define paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
raw_data_dir = os.path.join(base_dir, 'data', 'raw')
processed_data_dir = os.path.join(base_dir, 'data', 'processed')
final_data_dir = os.path.join(base_dir, 'data', 'final')
script_path = os.path.join(base_dir, 'airflow', 'include', 'assam_tenders_scraper.py')
transformation_script_path = os.path.join(base_dir, 'code', 'transformation_scripts', 'data_prep_ocds_mapping.py')

# Create directories task
create_directories = BashOperator(
    task_id='create_directories',
    bash_command='mkdir -p /opt/airflow/data/raw /opt/airflow/data/processed /opt/airflow/data/final',
    dag=dag,
)

# Scrape tenders task using direct scraper with interactive CAPTCHA handling
scrape_tenders = BashOperator(
    task_id='scrape_tenders',
    bash_command='python /opt/airflow/include/direct_scraper.py --output-path /opt/airflow/data/raw --from-date {{ (execution_date - macros.timedelta(days=7)).strftime("%Y-%m-%d") }} --to-date {{ execution_date.strftime("%Y-%m-%d") }}',
    dag=dag,
)

# Check if data was scraped successfully
check_data_exists = FileSensor(
    task_id='check_data_exists',
    filepath='/opt/airflow/data/raw',  # Use the absolute container path
    poke_interval=60,  # Check every minute
    timeout=60 * 10,  # Timeout after 10 minutes
    mode='poke',
    dag=dag,
)

# Define data preprocessing function
def preprocess_data(**kwargs):
    """
    Preprocess the raw data before transformation.
    This function cleans the data and prepares it for the OCDS mapping.
    """
    import glob
    import pandas as pd
    
    # Get execution date
    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y%m%d')
    
    # Get all CSV files in the raw data directory
    csv_files = glob.glob('/opt/airflow/data/raw/**/*.csv', recursive=True)
    
    if not csv_files:
        raise ValueError("No CSV files found in the raw data directory")
    
    # Process each file
    for file_path in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Basic cleaning
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.fillna('')
            
            # Save the preprocessed data
            filename = os.path.basename(file_path)
            output_path = os.path.join('/opt/airflow/data/processed', f"preprocessed_{filename}")
            df.to_csv(output_path, index=False)
            
            print(f"Preprocessed {filename} and saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    return processed_data_dir

# Preprocess data task
preprocess_data_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

# Run the data transformation script
transform_data = BashOperator(
    task_id='transform_data',
    bash_command=f'python {transformation_script_path} --input-dir /opt/airflow/data/processed --output-dir /opt/airflow/data/final',
    dag=dag,
)

# Generate report on the processed data
def generate_report(**kwargs):
    """
    Generate a summary report of the processed data.
    """
    import glob
    import pandas as pd
    from datetime import datetime
    
    # Get execution date
    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y%m%d')
    
    # Get all CSV files in the final data directory
    csv_files = glob.glob('/opt/airflow/data/final/*.csv')
    
    if not csv_files:
        print("No CSV files found in the final data directory")
        return
    
    # Initialize report data
    report_data = {
        'filename': [],
        'record_count': [],
        'columns': [],
        'missing_values_pct': []
    }
    
    # Process each file
    for file_path in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Calculate statistics
            filename = os.path.basename(file_path)
            record_count = len(df)
            columns = list(df.columns)
            missing_values_pct = (df.isnull().sum() / record_count * 100).mean()
            
            # Add to report data
            report_data['filename'].append(filename)
            report_data['record_count'].append(record_count)
            report_data['columns'].append(len(columns))
            report_data['missing_values_pct'].append(missing_values_pct)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
    
    # Create report DataFrame
    report_df = pd.DataFrame(report_data)
    
    # Save the report
    report_path = os.path.join('/opt/airflow/data/final', f"data_quality_report_{date_str}.csv")
    report_df.to_csv(report_path, index=False)
    
    print(f"Generated data quality report: {report_path}")
    
    return report_path

# Generate report task
generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
create_directories >> scrape_tenders >> check_data_exists >> preprocess_data_task >> transform_data >> generate_report_task
