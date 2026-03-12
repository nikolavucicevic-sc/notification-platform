#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Notification Platform...${NC}"

# Start Docker containers
echo -e "${GREEN}Starting Docker containers (postgres, rabbitmq, wiremock)...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${GREEN}Waiting for Docker services to be ready...${NC}"
echo "Waiting for RabbitMQ..."
until curl -s -u admin:admin http://localhost:15672/api/overview > /dev/null 2>&1; do
    sleep 1
done
echo "RabbitMQ is ready!"
sleep 2

# Start notification-service
echo -e "${GREEN}Starting notification-service on port 8002...${NC}"
cd notification-service
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002 > ../logs/notification-service.log 2>&1 &
NOTIFICATION_PID=$!
echo "notification-service started (PID: $NOTIFICATION_PID)"
cd ..

# Start customer-service
echo -e "${GREEN}Starting customer-service on port 8001...${NC}"
cd customer-service
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 > ../logs/customer-service.log 2>&1 &
CUSTOMER_PID=$!
echo "customer-service started (PID: $CUSTOMER_PID)"
cd ..

# Start email-sender
echo -e "${GREEN}Starting email-sender...${NC}"
cd email-sender
source ../.venv/bin/activate
PYTHONPATH=. python -m app.main > ../logs/email-sender.log 2>&1 &
EMAIL_PID=$!
echo "email-sender started (PID: $EMAIL_PID)"
cd ..

# Start frontend
echo -e "${GREEN}Starting frontend on port 3000...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "frontend started (PID: $FRONTEND_PID)"
cd ..

# Save PIDs to file for easy stopping
echo "$NOTIFICATION_PID" > .pids
echo "$CUSTOMER_PID" >> .pids
echo "$EMAIL_PID" >> .pids
echo "$FRONTEND_PID" >> .pids

echo -e "${BLUE}All services started!${NC}"
echo ""
echo "Services running:"
echo "  - PostgreSQL:          http://localhost:5432"
echo "  - RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo "  - Wiremock:            http://localhost:8089"
echo "  - Customer Service:    http://localhost:8001"
echo "  - Notification Service: http://localhost:8002"
echo "  - Frontend:            http://localhost:3000"
echo ""
echo "Logs are in ./logs/ directory"
echo "To stop all services, run: ./stop-all.sh"
