#!/bin/bash

# Script to run all tests locally

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Running Tests for Notification Platform"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_dir=$2

    echo -e "\n${BLUE}Testing $service_name...${NC}"
    cd "$SCRIPT_DIR/$service_dir"

    if pytest -v --cov=app --cov-report=term-missing --cov-report=html; then
        echo -e "${GREEN}✓ $service_name tests passed${NC}"
    else
        echo -e "${RED}✗ $service_name tests failed${NC}"
        cd "$SCRIPT_DIR"
        exit 1
    fi
}

# Run tests for each service
run_service_tests "Customer Service" "customer-service"
run_service_tests "Notification Service" "notification-service"
run_service_tests "Email Sender" "email-sender"

cd "$SCRIPT_DIR"

echo -e "\n${GREEN}========================================"
echo "All tests passed successfully!"
echo "========================================${NC}"

echo -e "\nCoverage reports generated in each service's htmlcov/ directory"
echo "Open htmlcov/index.html in a browser to view detailed coverage"