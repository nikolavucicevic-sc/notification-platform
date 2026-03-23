##🚨 EC2 Out of Memory (OOM) Issue - Complete Fix

## Problem Diagnosis

Your EC2 instance is running **OUT OF MEMORY**, causing:
```
Out of memory: Killed process 34284 (beam.smp) total-vm:2274832kB
```

**`beam.smp`** = RabbitMQ's Erlang VM process was killed by the Linux kernel!

---

## Root Causes

1. **Too many services running** (6 Docker containers)
2. **No memory limits set** (containers can use all available RAM)
3. **No swap space** (no virtual memory buffer)
4. **Small EC2 instance** (likely t2.micro/t2.small with 1-2GB RAM)

---

## Solutions Implemented

### ✅ Solution 1: Added Memory Limits to Docker Compose

Updated `docker-compose.yml` with memory constraints:

```yaml
Service Memory Allocation:
- PostgreSQL:      256MB limit, 128MB reserved
- RabbitMQ:        512MB limit, 256MB reserved (biggest consumer)
- Wiremock:        128MB limit,  64MB reserved
- Customer Service: 256MB limit, 128MB reserved
- Notification Svc: 256MB limit, 128MB reserved
- Email Sender:    256MB limit, 128MB reserved
- Frontend:        128MB limit,  64MB reserved

Total Reserved: ~1.1GB
Total Limit:    ~2GB
```

**RabbitMQ specific optimization:**
```yaml
environment:
  RABBITMQ_VM_MEMORY_HIGH_WATERMARK: 0.4
```
This prevents RabbitMQ from using more than 40% of its limit.

---

## Step-by-Step Fix Instructions

### Step 1: Check Your EC2 Instance Type

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Check instance type and memory
curl -s http://169.254.169.254/latest/meta-data/instance-type
free -h
```

**Recommended minimum:** t2.small (2GB RAM) or t3.small (2GB RAM)
**If using t2.micro (1GB):** Upgrade to t2.small!

---

### Step 2: Add Swap Space (IMPORTANT!)

Swap provides virtual memory when RAM is full.

```bash
# On EC2 instance
cd ~/notification-platform
sudo bash add-swap.sh
```

This will:
- Create 2GB swap file
- Make it permanent across reboots
- Optimize swap settings

**Verify swap:**
```bash
free -h
swapon --show
```

Expected output:
```
NAME      TYPE SIZE USED PRIO
/swapfile file   2G   0B   -2
```

---

### Step 3: Deploy Updated Docker Compose

#### Option A: Automatic (if GitHub Secrets are fixed)
```bash
# On your local machine
git add docker-compose.yml add-swap.sh diagnose-ec2.sh OOM_FIX.md
git commit -m "Add memory limits and swap configuration to fix OOM

- Added memory limits to all Docker containers
- RabbitMQ limited to 512MB with 40% watermark
- Created swap space script for EC2
- Total memory usage capped at ~2GB

Fixes: Out of Memory crashes"
git push origin main
```

#### Option B: Manual Deploy
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Navigate to project
cd notification-platform

# Pull latest changes
git pull origin main

# Stop all containers
docker compose down

# Remove old images to free space
docker system prune -af --volumes

# Start with new memory limits
docker compose up -d --build

# Watch logs
docker compose logs -f
```

---

### Step 4: Monitor Memory Usage

```bash
# Real-time memory monitoring
watch -n 2 free -h

# Docker container memory usage
docker stats

# Check for OOM events
dmesg | grep -i "out of memory"

# Run diagnostic script
bash diagnose-ec2.sh > diagnostics.log
```

---

## Memory Budget Breakdown

### For 2GB EC2 Instance (t2.small)

```
System Reserved:     ~300MB  (OS, kernel, etc.)
Swap Available:      2GB     (virtual memory)

Docker Containers:
├── PostgreSQL       256MB (limit)
├── RabbitMQ         512MB (limit) ⚠️ Biggest consumer
├── Wiremock         128MB (limit)
├── Customer Svc     256MB (limit)
├── Notification Svc 256MB (limit)
├── Email Sender     256MB (limit)
└── Frontend         128MB (limit)
────────────────────────────
Total Docker:        ~1.8GB

Available Headroom:  ~200MB + 2GB swap
```

**This should work reliably!**

---

## Verification Checklist

After deploying, verify everything is working:

### ✅ 1. Check Swap
```bash
free -h
# Should show swap space
```

### ✅ 2. Check All Containers Running
```bash
docker ps
# All 6 containers should be "Up" and "healthy"
```

### ✅ 3. Check Memory Usage
```bash
docker stats --no-stream
# No container should exceed its limit
```

### ✅ 4. Check RabbitMQ Memory
```bash
docker exec notification-rabbitmq rabbitmq-diagnostics memory_breakdown
```

### ✅ 5. Test the Application
```bash
# Health checks
curl http://your-ec2-ip:8001/health  # Customer service
curl http://your-ec2-ip:8002/health  # Notification service
curl http://your-ec2-ip:3000         # Frontend
```

### ✅ 6. Monitor Logs
```bash
docker compose logs -f --tail=100
# Should see:
# - "✓ Database connection established"
# - "✓ RabbitMQ connection established"
# - No OOM errors
```

---

## If Still Having Issues

### Option 1: Reduce Frontend (if not needed)
```yaml
# Comment out frontend temporarily
# frontend:
#   ...
```

### Option 2: Increase EC2 Instance Size
```bash
# Stop instance
# Change instance type to t2.medium (4GB RAM)
# Start instance
```

### Option 3: Use External RabbitMQ
Consider using CloudAMQP or AWS MQ instead of self-hosted RabbitMQ.

---

## Prevention for Future

### 1. Set up Monitoring
```bash
# Install monitoring
sudo apt-get install -y prometheus-node-exporter

# Or use CloudWatch
aws cloudwatch put-metric-data ...
```

### 2. Set up Alerts
- Alert when memory > 80%
- Alert when swap usage > 50%
- Alert on OOM events

### 3. Regular Cleanup
```bash
# Weekly cleanup cron job
0 2 * * 0 docker system prune -af --volumes
```

---

## Why This Happens

**Docker's Default Behavior:**
- No memory limits = containers can use ALL available RAM
- RabbitMQ is memory-hungry (can easily use 1GB+)
- Multiple containers compete for resources
- Linux kernel kills processes when RAM exhausted

**Our Fix:**
- Hard limits prevent runaway memory usage
- Swap provides buffer for temporary spikes
- RabbitMQ watermark prevents excessive growth
- Monitored and predictable resource usage

---

## Quick Reference Commands

```bash
# Check memory
free -h

# Check swap
swapon --show

# Check Docker memory
docker stats --no-stream

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View OOM events
dmesg | grep -i "out of memory"

# Restart all services
docker compose restart

# Hard reset
docker compose down && docker compose up -d

# Check RabbitMQ memory
docker exec notification-rabbitmq rabbitmqctl status | grep -A 5 memory
```

---

## Expected Results After Fix

✅ **Before:**
- RabbitMQ crashes randomly
- Services can't connect
- System becomes unresponsive
- OOM killer triggers

✅ **After:**
- All containers stay within limits
- Swap handles temporary spikes
- System remains stable
- No OOM events

---

## Summary

**Problem:** EC2 instance running out of memory, killing RabbitMQ

**Fix:**
1. Added memory limits to all containers (✅ Done in code)
2. Add 2GB swap space (⏸️ Need to run on EC2)
3. Consider upgrading to t2.small if on t2.micro (💡 Recommended)

**Next Steps:**
1. SSH to EC2
2. Run `sudo bash add-swap.sh`
3. Pull latest code (`git pull`)
4. Restart containers (`docker compose up -d`)
5. Monitor (`docker stats`)

Your system should now be stable! 🎉
