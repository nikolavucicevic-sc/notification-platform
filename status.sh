#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Notification Platform Status"
echo "============================"
echo ""

# Check Docker services
echo "Docker Services:"
docker-compose ps

echo ""
echo "Application Services:"

# Check if services are running
check_service() {
    local name=$1
    local port=$2
    local pid_line=$3

    if [ -f .pids ]; then
        pid=$(sed -n "${pid_line}p" .pids)
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name (PID: $pid, Port: $port)"
        else
            echo -e "  ${RED}✗${NC} $name (not running)"
        fi
    else
        # Check by port
        if lsof -i:$port > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name (Port: $port)"
        else
            echo -e "  ${RED}✗${NC} $name (not running)"
        fi
    fi
}

check_service "Notification Service" 8002 1
check_service "Customer Service" 8001 2
check_service "Email Sender" "-" 3
check_service "Frontend" 3000 4

echo ""
echo "Service URLs:"
echo "  - Frontend:            http://localhost:3000"
echo "  - Notification API:    http://localhost:8002/docs"
echo "  - Customer API:        http://localhost:8001/docs"
echo "  - RabbitMQ Management: http://localhost:15672"
