#!/bin/bash

echo "========================================="
echo "Frontend Diagnostics"
echo "========================================="
echo ""

echo "1. Checking Docker containers..."
docker ps -a | grep -E "CONTAINER|frontend"
echo ""

echo "2. Checking frontend container logs (last 30 lines)..."
docker logs notification-frontend --tail 30
echo ""

echo "3. Checking if port 3000 is listening..."
netstat -tuln | grep 3000 || ss -tuln | grep 3000
echo ""

echo "4. Checking frontend container health..."
docker inspect notification-frontend --format='{{.State.Status}}' 2>/dev/null || echo "Container not found"
echo ""

echo "5. Checking nginx config inside container (if running)..."
docker exec notification-frontend cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "Cannot read nginx config (container may not be running)"
echo ""

echo "6. Testing internal connectivity..."
curl -I http://localhost:3000 --max-time 2 2>&1 || echo "Cannot connect to localhost:3000"
echo ""

echo "7. Checking Docker Compose services..."
docker compose ps
echo ""

echo "========================================="
echo "Action Items:"
echo "========================================="
echo "If container is not running:"
echo "  - Run: docker compose up frontend -d --build"
echo ""
echo "If port 3000 is not open in Security Group:"
echo "  - Go to EC2 Console > Security Groups"
echo "  - Add Inbound Rule: Type=Custom TCP, Port=3000, Source=0.0.0.0/0"
echo ""
echo "If container keeps restarting:"
echo "  - Check logs: docker logs notification-frontend"
echo "  - Rebuild: docker compose build frontend && docker compose up frontend -d"
