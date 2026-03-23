#!/bin/bash
# EC2 Memory and Docker Diagnostics Script

echo "=========================================="
echo "EC2 Instance Diagnostics"
echo "=========================================="

echo ""
echo "1. SYSTEM MEMORY:"
echo "-------------------"
free -h

echo ""
echo "2. DISK USAGE:"
echo "-------------------"
df -h

echo ""
echo "3. SWAP SPACE:"
echo "-------------------"
swapon --show || echo "No swap space configured"

echo ""
echo "4. DOCKER CONTAINERS STATUS:"
echo "-------------------"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.State}}"

echo ""
echo "5. DOCKER MEMORY USAGE:"
echo "-------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "6. TOP MEMORY CONSUMERS:"
echo "-------------------"
ps aux --sort=-%mem | head -10

echo ""
echo "7. DOCKER LOGS (last 50 lines per service):"
echo "-------------------"
for container in $(docker ps -a --format "{{.Names}}"); do
    echo ""
    echo "=== $container ==="
    docker logs --tail 50 $container 2>&1
done

echo ""
echo "8. SYSTEM LOAD:"
echo "-------------------"
uptime

echo ""
echo "9. DMESG OOM EVENTS:"
echo "-------------------"
dmesg | grep -i "out of memory" | tail -5

echo ""
echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
