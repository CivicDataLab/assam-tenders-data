# Docker Setup for Assam Tenders Data Scraper

This repository contains a Docker setup for running the Assam Tenders Data Scraper with Apache Airflow.

## Quick Start

1. Start the Airflow environment:
   ```
   ./start_airflow_mac.sh
   ```

2. Access the Airflow UI:
   - URL: http://localhost:8080
   - Username: admin
   - Password: admin123

3. If you need to reset the admin password:
   ```
   ./reset_airflow_password.sh
   ```

4. To stop all services:
   ```
   docker compose down
   ```

5. To start with a clean setup (removes existing containers and volumes):
   ```
   ./start_airflow_mac.sh clean
   ```

## Available Services

- **Airflow Webserver**: http://localhost:8080
- **Selenium Chrome UI**: http://localhost:7900 (password: secret)

## Testing Selenium Connection

To test the Selenium connection:
```
docker compose exec airflow-webserver python /opt/airflow/scripts/selenium_test.py
```

## Troubleshooting

For troubleshooting, view the logs:
```
docker compose logs
```

## Docker Directory Documentation


### Docker README

# Docker Setup for Assam Tenders Scraper

This directory contains the Docker configuration for running the Assam Tenders Scraper with Apache Airflow.

> **Note:** The scripts automatically detect whether to use the newer `docker compose` syntax or the legacy `docker-compose` command based on what's available on your system.

## Overview

The Docker setup includes:

- Apache Airflow with PostgreSQL backend
- Redis for Celery executor
- Chrome and ChromeDriver for Selenium-based web scraping
- EasyOCR and dependencies for CAPTCHA solving

## File Structure

- `Dockerfile`: Custom Docker image for Airflow with all necessary dependencies
- `requirements.txt`: Python packages required for the Assam Tenders Scraper

## Requirements

- Docker Engine (version 19.03.0+)
- Docker Compose (version 1.27.0+)
- At least 4GB of RAM allocated to Docker
- At least 10GB of free disk space

## Quick Start

To set up and start the Docker environment, run:

```bash
# From the project root directory
./setup_docker.sh
```

This script will:
1. Create necessary directories
2. Set appropriate permissions
3. Build the Docker images
4. Initialize the Airflow database
5. Set up the default user

## Manual Setup

If you prefer to set up manually:

1. Make sure you have the necessary directories:
   ```bash
   mkdir -p ./data/raw ./data/processed ./data/final ./data/archive ./airflow/logs
   ```

2. Set the proper permissions:
   ```bash
   export AIRFLOW_UID=$(id -u)
   export AIRFLOW_GID=$(id -g)
   ```

3. Update the `.env` file with your user ID:
   ```bash
   sed -i "s/^AIRFLOW_UID=.*/AIRFLOW_UID=${AIRFLOW_UID}/" .env
   ```

4. Build the Docker images:
   ```bash
   # Using newer Docker Compose syntax
   docker compose build
   
   # OR using legacy Docker Compose syntax
   docker-compose build
   ```

5. Initialize Airflow:
   ```bash
   # Using newer Docker Compose syntax
   docker compose up airflow-init
   
   # OR using legacy Docker Compose syntax
   docker-compose up airflow-init
   ```

6. Start all services:
   ```bash
   # Using newer Docker Compose syntax
   docker compose up -d
   
   # OR using legacy Docker Compose syntax
   docker-compose up -d
   ```

## Accessing the Services

- **Airflow UI**: http://localhost:8080 (default credentials: airflow/airflow)
- **Flower** (Celery monitoring): http://localhost:5555

## Customization

### Environment Variables

You can customize the deployment by editing the `.env` file. Important variables include:

- `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`: Credentials for the Airflow UI
- `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL credentials
- `AIRFLOW__CORE__LOAD_EXAMPLES`: Set to 'False' to avoid loading example DAGs

### Adding New Dependencies

If you need to add new Python dependencies, update the `requirements.txt` file and rebuild the Docker image:

```bash
# Using newer Docker Compose syntax
docker compose build --no-cache
docker compose up -d

# OR using legacy Docker Compose syntax
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### Common Issues

- **Permissions Problems**: Ensure `AIRFLOW_UID` in `.env` matches your host user ID
- **Memory Issues**: Increase memory allocated to Docker
- **Selenium Errors**: The Dockerfile is configured for Chrome; adjust if another browser is needed

### Logs

To check logs for any service:

```bash
# View logs for the webserver (newer Docker Compose syntax)
docker compose logs airflow-webserver
# OR using legacy Docker Compose syntax
docker-compose logs airflow-webserver

# View logs for the scheduler (newer Docker Compose syntax)
docker compose logs airflow-scheduler
# OR using legacy Docker Compose syntax
docker-compose logs airflow-scheduler
```

## Data Persistence

All data is persisted in Docker volumes and host-mounted directories:

- Database: PostgreSQL data is stored in a Docker volume
- Airflow data: DAGs, logs, and plugins are mounted from the host
- Scraped data: Stored in the mounted `./data` directory
### Docker Troubleshooting

# Docker Setup Troubleshooting Guide

This guide provides solutions for common issues encountered when setting up the Docker environment for the Assam Tenders Data Scraper.

## Chrome Installation Issues

### Error: Unable to locate package google-chrome-stable

**Problem**: During Docker build, you see an error like:
```
E: Unable to locate package google-chrome-stable
```

**Solution**:
1. The Dockerfile has been updated to download Chrome directly instead of using the apt repository.
2. Try rebuilding the image with:
   ```bash
   ./setup_docker.sh
   ```
3. If the issue persists, manually edit the Dockerfile to use a specific Chrome version:
   ```dockerfile
   # Find Chrome version that works with your system
   RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
       && apt-get install -y ./google-chrome-stable_current_amd64.deb
   ```

## Python Package Installation Issues

### EasyOCR Installation Failures

**Problem**: Issues installing EasyOCR and its dependencies.

**Solution**:
1. Requirements have been pinned to specific versions for compatibility.
2. If you encounter GPU-related errors, modify `requirements.txt` to use CPU-only versions:
   ```
   # Replace
   torch==2.0.1
   torchvision==0.15.2
   # With
   torch==2.0.1+cpu
   torchvision==0.15.2+cpu
   -f https://download.pytorch.org/whl/torch_stable.html
   ```

## Docker Compose Command Issues

### Command Not Found

**Problem**: `docker-compose` command not found or not recognized.

**Solution**:
1. The scripts automatically detect whether to use `docker compose` or `docker-compose`.
2. If you're still having issues, specify the Docker Compose command directly:
   ```bash
   # For newer Docker versions:
   docker compose build
   docker compose up airflow-init
   docker compose up -d
   
   # For older Docker versions with standalone docker-compose:
   docker-compose build
   docker-compose up airflow-init
   docker-compose up -d
   ```

## Permission Issues

### Permission Denied Errors

**Problem**: You see permission errors when containers try to access mounted volumes.

**Solution**:
1. Run the setup script again to set the correct user ID:
   ```bash
   ./setup_docker.sh
   ```
2. Manually set permissions on data directories:
   ```bash
   sudo chown -R $(id -u):$(id -g) ./data
   sudo chown -R $(id -u):$(id -g) ./airflow/logs
   ```
3. Update the .env file with your user ID:
   ```
   AIRFLOW_UID=$(id -u)
   ```

## Networking Issues

### Cannot Connect to PostgreSQL

**Problem**: Airflow services cannot connect to the PostgreSQL database.

**Solution**:
1. Verify all containers are running:
   ```bash
   docker compose ps
   ```
2. Check PostgreSQL logs:
   ```bash
   docker compose logs postgres
   ```
3. Ensure the PostgreSQL credentials in `.env` match those in `docker-compose.yml`

### Port Conflicts

**Problem**: Airflow webserver fails to start due to port conflicts.

**Solution**:
1. Check if port 8080 is already in use:
   ```bash
   sudo lsof -i :8080
   ```
2. If so, modify the port mapping in `docker-compose.yml`:
   ```yaml
   airflow-webserver:
     ports:
       - "8081:8080"  # Change 8080 to another port
   ```

## Resource Issues

### Container Crashes Due to Memory Limits

**Problem**: Containers crash due to insufficient memory.

**Solution**:
1. Increase Docker's memory allocation (recommended at least 4GB)
2. Add memory limits to services in `docker-compose.yml`:
   ```yaml
   airflow-worker:
     deploy:
       resources:
         limits:
           memory: 2G
   ```

## Selenium/Chrome Issues in Containers

### Chrome Crashes or Behaves Unexpectedly

**Problem**: Chrome crashes during web scraping operations.

**Solution**:
1. Ensure ChromeDriver matches Chrome version
2. Add these Chrome options in your scraper code:
   ```python
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--disable-dev-shm-usage')
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--disable-gpu')
   ```

## Initialization Issues

### airflow-init Container Fails

**Problem**: The `airflow-init` container fails with errors.

**Solution**:
1. Check the initialization logs:
   ```bash
   docker compose logs airflow-init
   ```
2. If you see database connection issues, ensure PostgreSQL is running:
   ```bash
   docker compose up -d postgres
   docker compose ps postgres
   ```
3. Clean existing state and try again:
   ```bash
   docker compose down -v
   ./setup_docker.sh
   ```

## Complete Reset

If all else fails, perform a complete reset:

```bash
# Stop all containers and remove volumes
docker compose down -v

# Remove any dangling images
docker image prune -a

# Clear your data directories (optional - will lose data!)
rm -rf ./data/*
rm -rf ./airflow/logs/*

# Start again with the setup script
./setup_docker.sh
```

## Get Detailed Logs

To get more detailed logs for debugging:

```bash
# View logs from all services
docker compose logs

# View logs from a specific service with timestamps
docker compose logs --timestamps airflow-worker

# Follow logs in real-time
docker compose logs -f

# View logs only from the last 100 lines
docker compose logs --tail=100
```