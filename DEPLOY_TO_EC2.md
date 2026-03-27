# Quick Deploy to EC2

Your EC2 instance is running old code. Here's how to update it:

## SSH into EC2

```bash
ssh -i your-key.pem ubuntu@18.156.176.60
```

## Update and Restart

```bash
cd ~/notification-platform

# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs -f notification-service
```

## If You See Import Errors

The new code requires additional dependencies. Make sure Docker rebuilds:

```bash
# Force rebuild without cache
docker-compose build --no-cache notification-service
docker-compose up -d

# Verify it's working
curl http://localhost:8002/health
```

## Quick Fix (If Above Doesn't Work)

```bash
# Stop everything
docker-compose down

# Remove old images
docker system prune -a -f

# Rebuild from scratch
docker-compose up --build -d

# Wait 30 seconds for services to start
sleep 30

# Test
curl http://localhost:3000/api/health
```

## Verify It's Working

```bash
# Should return healthy status
curl http://localhost:8002/health | jq .

# Should return login page
curl http://localhost:3000
```

## If Still Not Working

Check the logs for specific errors:

```bash
# Notification service logs
docker-compose logs notification-service --tail 100

# All services
docker-compose logs --tail 50
```

## Common Issues

### Issue: ModuleNotFoundError: No module named 'structlog'

**Solution:** Dependencies not installed. Rebuild:
```bash
docker-compose build --no-cache notification-service
docker-compose up -d
```

### Issue: 502 Bad Gateway

**Solution:** Service crashed. Check logs and rebuild:
```bash
docker-compose logs notification-service
docker-compose restart notification-service
```

### Issue: Can't pull from GitHub

**Solution:** Setup GitHub access or use HTTPS:
```bash
cd ~/notification-platform
git remote set-url origin https://github.com/nikolavucicevic-sc/notification-platform.git
git pull origin main
```
