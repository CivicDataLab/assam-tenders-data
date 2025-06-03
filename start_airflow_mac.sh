#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Airflow for Apple Silicon Mac${NC}"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Determine Docker Compose command to use
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}Using Docker Compose command: ${DOCKER_COMPOSE}${NC}"

# Handle command line options
CLEAN=false

for arg in "$@"; do
    case $arg in
        clean)
            CLEAN=true
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $arg${NC}"
            echo -e "Available options: clean"
            ;;
    esac
done

# Clean up existing containers if requested
if [ "$CLEAN" = true ]; then
    echo -e "${YELLOW}Cleaning up Docker containers and volumes...${NC}"
    $DOCKER_COMPOSE -f docker-compose.mac.yml down -v
    docker system prune -f
fi

# Create necessary directories
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p ./data/raw
mkdir -p ./data/processed
mkdir -p ./data/final
mkdir -p ./data/archive
mkdir -p ./data/screenshots
mkdir -p ./airflow/logs
mkdir -p ./scripts

# Create a simple Selenium test script
echo -e "${GREEN}Creating Selenium test script...${NC}"
mkdir -p ./scripts
cat > ./scripts/selenium_test.py << EOF
#!/usr/bin/env python3
"""
Simple test script to verify Selenium connection
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Starting Selenium test...")

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    # Connect to remote Selenium server
    print("Connecting to Selenium Chrome...")
    driver = webdriver.Remote(
        command_executor='http://selenium-chrome:4444/wd/hub',
        options=chrome_options
    )
    
    # Navigate to a simple page
    print("Navigating to example.com...")
    driver.get("https://example.com")
    
    # Wait for page to load
    time.sleep(2)
    
    # Get page title
    title = driver.title
    print(f"Page title: {title}")
    
    # Get page content
    h1_text = driver.find_element(By.TAG_NAME, "h1").text
    print(f"H1 content: {h1_text}")
    
    # Take screenshot
    driver.save_screenshot("/opt/airflow/data/screenshots/test_screenshot.png")
    print("Screenshot saved to /opt/airflow/data/screenshots/test_screenshot.png")
    
    # Close browser
    driver.quit()
    print("Selenium test completed successfully!")
    
except Exception as e:
    print(f"Error during Selenium test: {e}")
    exit(1)
EOF
chmod +x ./scripts/selenium_test.py

# Start the services
echo -e "${GREEN}Starting Airflow services...${NC}"
$DOCKER_COMPOSE -f docker-compose.mac.yml up -d

echo -e "${GREEN}Waiting for services to be ready...${NC}"
sleep 10

echo -e "${GREEN}Services started!${NC}"
echo ""
echo -e "${GREEN}Access the Airflow UI at:${NC} http://localhost:8080"
echo -e "${GREEN}Username:${NC} admin"
echo -e "${GREEN}Password:${NC} admin"
echo ""
echo -e "${GREEN}Services available:${NC}"
echo -e "- Airflow Webserver: ${YELLOW}http://localhost:8080${NC}"
echo -e "- Selenium Chrome UI: ${YELLOW}http://localhost:7900${NC} (password: secret)"
echo ""
echo -e "${YELLOW}For troubleshooting, use: ${DOCKER_COMPOSE} -f docker-compose.mac.yml logs${NC}"
echo -e "${GREEN}To test Selenium connection:${NC} ${DOCKER_COMPOSE} -f docker-compose.mac.yml exec airflow-webserver python /opt/airflow/scripts/selenium_test.py"
echo -e "${GREEN}To stop all services:${NC} ${DOCKER_COMPOSE} -f docker-compose.mac.yml down"
echo -e "${GREEN}For a clean start:${NC} ./start_airflow_mac.sh clean"
