#!/bin/bash

# Color codes for output
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping Notification Platform...${NC}"

# Kill all Python and Node processes
if [ -f .pids ]; then
    echo -e "${RED}Stopping application services...${NC}"
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Killing process $pid"
            kill $pid
        fi
    done < .pids
    rm .pids
else
    echo "No .pids file found, attempting to find and kill services..."
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "python -m app.main" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
fi

# Stop Docker containers
echo -e "${RED}Stopping Docker containers...${NC}"
docker-compose down

echo -e "${BLUE}All services stopped!${NC}"
