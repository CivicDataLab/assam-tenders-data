from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os
import shutil
import glob

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
    'data_maintenance',
    default_args=default_args,
    description='Maintenance tasks for data management',
    schedule_interval='0 1 * * 0',  # Run at 1 AM every Sunday
    start_date=days_ago(1),
    catchup=False,
    tags=['maintenance', 'cleanup', 'monitoring'],
)

# Define paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
data_dir = os.path.join(base_dir, 'data')
raw_data_dir = os.path.join(data_dir, 'raw')
processed_data_dir = os.path.join(data_dir, 'processed')
final_data_dir = os.path.join(data_dir, 'final')
archive_dir = os.path.join(data_dir, 'archive')

# Create archive directory task
create_archive_dir = BashOperator(
    task_id='create_archive_dir',
    bash_command=f'mkdir -p {archive_dir}',
    dag=dag,
)

# Define data archiving function
def archive_old_data(**kwargs):
    """
    Archive data files older than 30 days to reduce storage usage.
    """
    # Get execution date
    execution_date = kwargs['execution_date']
    archive_date = execution_date.strftime('%Y%m%d')
    
    # Create archive subdirectory for this run
    archive_subdir = os.path.join(archive_dir, f'archive_{archive_date}')
    os.makedirs(archive_subdir, exist_ok=True)
    
    # Get all CSV files in the raw data directory
    raw_files = glob.glob(os.path.join(raw_data_dir, '**/*.csv'), recursive=True)
    processed_files = glob.glob(os.path.join(processed_data_dir, '**/*.csv'), recursive=True)
    
    # Combine all files to check
    all_files = raw_files + processed_files
    
    # Archive files older than 30 days
    cutoff_date = execution_date - timedelta(days=30)
    archived_count = 0
    
    for file_path in all_files:
        file_stat = os.stat(file_path)
        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
        
        if file_mtime < cutoff_date:
            # Determine the relative path structure to maintain in archive
            if file_path.startswith(raw_data_dir):
                rel_path = os.path.relpath(file_path, raw_data_dir)
                archive_path = os.path.join(archive_subdir, 'raw', rel_path)
            else:
                rel_path = os.path.relpath(file_path, processed_data_dir)
                archive_path = os.path.join(archive_subdir, 'processed', rel_path)
            
            # Create directory structure in archive
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            # Move file to archive
            shutil.move(file_path, archive_path)
            archived_count += 1
    
    print(f"Archived {archived_count} files older than 30 days to {archive_subdir}")
    return archived_count

# Archive old data task
archive_old_data_task = PythonOperator(
    task_id='archive_old_data',
    python_callable=archive_old_data,
    provide_context=True,
    dag=dag,
)

# Define disk usage check function
def check_disk_usage(**kwargs):
    """
    Check disk usage of data directories and log warnings if usage is high.
    """
    import shutil
    
    # Define threshold for warning (80% usage)
    threshold = 80
    
    # Check disk usage for each directory
    directories = [raw_data_dir, processed_data_dir, final_data_dir]
    warnings = []
    
    for directory in directories:
        if os.path.exists(directory):
            total, used, free = shutil.disk_usage(directory)
            usage_pct = (used / total) * 100
            
            print(f"Disk usage for {directory}: {usage_pct:.2f}%")
            
            if usage_pct > threshold:
                warning_msg = f"WARNING: High disk usage ({usage_pct:.2f}%) in {directory}"
                print(warning_msg)
                warnings.append(warning_msg)
    
    # Return warnings if any
    return '\n'.join(warnings) if warnings else "Disk usage is within acceptable limits."

# Check disk usage task
check_disk_usage_task = PythonOperator(
    task_id='check_disk_usage',
    python_callable=check_disk_usage,
    provide_context=True,
    dag=dag,
)

# Define data quality check function
def check_data_quality(**kwargs):
    """
    Perform basic data quality checks on the final data.
    """
    import pandas as pd
    import glob
    
    # Get execution date
    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y%m%d')
    
    # Get all CSV files in the final data directory
    csv_files = glob.glob(os.path.join(final_data_dir, '*.csv'))
    
    if not csv_files:
        print("No CSV files found in the final data directory")
        return "No data to check"
    
    # Initialize quality report
    quality_report = {
        'filename': [],
        'record_count': [],
        'duplicate_count': [],
        'missing_values_count': [],
        'issues': []
    }
    
    # Process each file
    for file_path in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Get filename
            filename = os.path.basename(file_path)
            
            # Check record count
            record_count = len(df)
            
            # Check for duplicates
            duplicate_count = len(df) - len(df.drop_duplicates())
            
            # Check for missing values
            missing_values_count = df.isnull().sum().sum()
            
            # Identify issues
            issues = []
            if duplicate_count > 0:
                issues.append(f"Contains {duplicate_count} duplicate records")
            if missing_values_count > 0:
                issues.append(f"Contains {missing_values_count} missing values")
            if record_count == 0:
                issues.append("Empty file")
            
            # Add to quality report
            quality_report['filename'].append(filename)
            quality_report['record_count'].append(record_count)
            quality_report['duplicate_count'].append(duplicate_count)
            quality_report['missing_values_count'].append(missing_values_count)
            quality_report['issues'].append('; '.join(issues) if issues else 'No issues')
            
        except Exception as e:
            print(f"Error checking {file_path}: {str(e)}")
            quality_report['filename'].append(filename)
            quality_report['record_count'].append(0)
            quality_report['duplicate_count'].append(0)
            quality_report['missing_values_count'].append(0)
            quality_report['issues'].append(f"Error: {str(e)}")
    
    # Create report DataFrame
    report_df = pd.DataFrame(quality_report)
    
    # Save the report
    report_path = os.path.join(final_data_dir, f"quality_check_report_{date_str}.csv")
    report_df.to_csv(report_path, index=False)
    
    print(f"Generated data quality check report: {report_path}")
    
    # Return summary
    total_issues = sum(1 for issues in quality_report['issues'] if issues != 'No issues')
    return f"Checked {len(csv_files)} files. Found issues in {total_issues} files. See {report_path} for details."

# Check data quality task
check_data_quality_task = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
create_archive_dir >> archive_old_data_task
check_disk_usage_task >> check_data_quality_task
