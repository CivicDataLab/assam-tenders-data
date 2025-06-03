#!/bin/bash
set -e

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
  local host="$1"
  local port="$2"
  local user="$3"
  local password="$4"
  local db="$5"
  
  echo "Waiting for PostgreSQL to be ready..."
  while ! nc -z "$host" "$port"; do
    sleep 1
  done
  
  echo "PostgreSQL is up"
}

# Initialize the Airflow database if it doesn't exist yet
initialize_airflow() {
  echo "Initializing Airflow..."
  airflow db init
  
  # Create admin user if it doesn't exist
  if airflow users list | grep -q 'admin'; then
    echo "Admin user already exists"
  else
    echo "Creating admin user..."
    airflow users create \
      --username admin \
      --password admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com
  fi
}

# Extract database connection details
if [[ -n "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN}" ]]; then
  DB_URI=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*//}
  DB_USER=${DB_URI%:*}
  DB_URI=${DB_URI#*:}
  DB_PASS=${DB_URI%@*}
  DB_URI=${DB_URI#*@}
  DB_HOST=${DB_URI%:*}
  DB_URI=${DB_URI#*:}
  DB_PORT=${DB_URI%/*}
  DB_URI=${DB_URI#*/}
  DB_NAME=${DB_URI%%\?*}
  
  # Wait for PostgreSQL
  wait_for_postgres "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASS" "$DB_NAME"
fi

# Initialize Airflow
initialize_airflow

# Check if we're starting the webserver or scheduler
if [[ "$1" == "webserver" ]]; then
  echo "Starting Airflow webserver..."
  exec airflow webserver
elif [[ "$1" == "scheduler" ]]; then
  echo "Starting Airflow scheduler..."
  exec airflow scheduler
elif [[ "$1" == "standalone" ]]; then
  echo "Starting Airflow in standalone mode..."
  airflow webserver &
  exec airflow scheduler
else
  # Execute the command provided as arguments
  exec "$@"
fi