#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "   Service Health Check"
echo "=================================="
echo ""

# Check Docker Compose services
echo "📦 Container Status:"
docker-compose ps
echo ""

# Check service endpoints
echo "🏥 Service Health Endpoints:"

services=(
    "notification-service:8002:http://localhost:8002/health"
    "customer-service:8001:http://localhost:8001/health"
    "scheduler-service:8003:http://localhost:8003/health"
    "template-service:8004:http://localhost:8004/health"
    "frontend:3000:http://localhost:3000/api/health/"
    "postgres:5432:postgres"
    "redis:6379:redis"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port url <<< "$service"

    if [ "$name" = "postgres" ]; then
        if docker exec notification-postgres pg_isready -U admin &>/dev/null; then
            echo -e "  ✅ ${GREEN}$name${NC} - Healthy"
        else
            echo -e "  ❌ ${RED}$name${NC} - Unhealthy"
        fi
    elif [ "$name" = "redis" ]; then
        if docker exec notification-redis redis-cli ping &>/dev/null; then
            echo -e "  ✅ ${GREEN}$name${NC} - Healthy"
        else
            echo -e "  ❌ ${RED}$name${NC} - Unhealthy"
        fi
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        if [ "$response" = "200" ]; then
            echo -e "  ✅ ${GREEN}$name${NC} - Healthy (HTTP $response)"
        elif [ "$response" = "307" ]; then
            echo -e "  ⚠️  ${YELLOW}$name${NC} - Redirect (HTTP $response)"
        else
            echo -e "  ❌ ${RED}$name${NC} - Unhealthy (HTTP $response)"
        fi
    fi
done

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10

echo ""
echo "🔍 Recent Errors (last 20 lines):"
docker-compose logs --tail 20 | grep -i error || echo "  No recent errors found"

echo ""
echo "=================================="
echo "Monitoring URLs:"
echo "  Frontend: http://3.74.152.191:3000"
echo "  Prometheus: http://3.74.152.191:9090"
echo "  Grafana: http://3.74.152.191:3001"
echo "  Jaeger: http://3.74.152.191:16686"
echo "=================================="
