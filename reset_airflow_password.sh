#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Resetting Airflow admin password${NC}"

# Determine Docker Compose command to use
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if containers are running
if ! $DOCKER_COMPOSE -f docker-compose.mac.yml ps | grep -q "airflow-webserver.*Up"; then
    echo -e "${RED}Airflow webserver is not running. Please start it first with ./start_airflow_mac.sh${NC}"
    exit 1
fi

# Set new password
NEW_PASSWORD="admin123"

# Reset the admin password
echo -e "${YELLOW}Resetting admin password to: ${NEW_PASSWORD}${NC}"
$DOCKER_COMPOSE -f docker-compose.mac.yml exec airflow-webserver airflow users delete -u admin || true
$DOCKER_COMPOSE -f docker-compose.mac.yml exec airflow-webserver airflow users create \
    -r Admin \
    -u admin \
    -e admin@example.com \
    -f Admin \
    -l User \
    -p "${NEW_PASSWORD}"

echo -e "${GREEN}Password reset successful!${NC}"
echo -e "${GREEN}You can now log in to the Airflow UI with:${NC}"
echo -e "${YELLOW}Username:${NC} admin"
echo -e "${YELLOW}Password:${NC} ${NEW_PASSWORD}"
