#!/bin/bash

echo "========================================="
echo "RabbitMQ Fix Script"
echo "========================================="
echo ""

echo "1. Checking current memory status..."
free -h
echo ""

echo "2. Checking swap status..."
swapon --show
echo ""

echo "3. Stopping all services..."
docker compose down
echo ""

echo "4. Checking if swap exists..."
if [ -f /swapfile ]; then
    echo "✓ Swap file exists"
    swapon --show
else
    echo "⚠️  No swap file found. Creating 2GB swap..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile

    # Make swap permanent
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi

    echo "✓ Swap created and enabled"
fi
echo ""

echo "5. Verifying swap is active..."
swapon --show
free -h
echo ""

echo "6. Cleaning up Docker resources..."
docker system prune -f
echo ""

echo "7. Starting services in order (postgres -> rabbitmq -> others)..."
echo "Starting postgres..."
docker compose up -d postgres
echo "Waiting for postgres to be healthy (30 seconds)..."
sleep 30
docker compose ps postgres
echo ""

echo "Starting RabbitMQ..."
docker compose up -d rabbitmq
echo "Waiting for RabbitMQ to be healthy (45 seconds)..."
sleep 45
docker compose ps rabbitmq
echo ""

echo "Starting other services..."
docker compose up -d
echo ""

echo "8. Checking all services..."
docker compose ps
echo ""

echo "9. Checking RabbitMQ logs..."
docker logs notification-rabbitmq --tail 20
echo ""

echo "10. Checking memory usage..."
docker stats --no-stream
echo ""

echo "========================================="
echo "Summary"
echo "========================================="
docker compose ps | grep -E "NAME|rabbitmq|frontend"
echo ""

echo "If RabbitMQ is still unhealthy:"
echo "1. Check logs: docker logs notification-rabbitmq"
echo "2. Try increasing memory: Edit docker-compose.yml, increase RabbitMQ memory limit to 768M"
echo "3. Restart: docker compose restart rabbitmq"
echo ""

echo "Frontend should be accessible at: http://$(curl -s ifconfig.me):3000"
