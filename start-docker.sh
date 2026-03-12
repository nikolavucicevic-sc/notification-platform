#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Notification Platform with Docker...${NC}"

# Stop current services if running
echo -e "${YELLOW}Stopping any running local services...${NC}"
./stop-all.sh 2>/dev/null || true

# Build and start all services
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose up --build -d

echo ""
echo -e "${BLUE}Waiting for services to be ready...${NC}"
echo -e "${GREEN}This may take a minute on first run...${NC}"

# Wait for services
sleep 5

echo ""
echo -e "${BLUE}Checking service health...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}All services started!${NC}"
echo ""
echo "Services available at:"
echo "  - Frontend:            http://localhost:3000"
echo "  - Notification Service: http://localhost:8002/docs"
echo "  - Customer Service:    http://localhost:8001/docs"
echo "  - RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo "  - Wiremock:            http://localhost:8089"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f                    # All services"
echo "  docker-compose logs -f notification-service"
echo "  docker-compose logs -f email-sender"
echo "  docker-compose logs -f frontend"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
