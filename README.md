# Notification Platform

A microservices-based notification platform with email sending capabilities, built with FastAPI, React, and RabbitMQ.

## Architecture

- **notification-service** (port 8002) - Main service for creating and managing notifications
- **customer-service** (port 8001) - Customer management service
- **email-sender** - Background service for sending emails via RabbitMQ
- **frontend** (port 3000) - React + TypeScript UI
- **PostgreSQL** (port 5432) - Database
- **RabbitMQ** (port 5672, management UI: 15672) - Message broker
- **Wiremock** (port 8089) - Email API mock

## Quick Start

### Option 1: Docker (Recommended)

**Requirements:**
- Docker
- Docker Compose

**Start everything:**
```bash
./start-docker.sh
```

Or manually:
```bash
docker-compose up --build -d
```

**View logs:**
```bash
docker-compose logs -f                      # All services
docker-compose logs -f notification-service # Specific service
docker-compose logs -f email-sender
docker-compose logs -f frontend
```

**Stop everything:**
```bash
docker-compose down
```

**Stop and remove volumes (reset database):**
```bash
docker-compose down -v
```

### Option 2: Local Development

**Requirements:**
- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL, RabbitMQ, Wiremock only)

**First Time Setup:**

1. Install dependencies:
```bash
# Python virtual environment (if not exists)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r notification-service/requirements.txt
pip install -r customer-service/requirements.txt
pip install -r email-sender/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

2. Start infrastructure only:
```bash
docker-compose up -d postgres rabbitmq wiremock
```

3. Start all application services:
```bash
./start-all.sh
```

**Daily Usage:**

**Start everything:**
```bash
./start-all.sh
```

**Stop everything:**
```bash
./stop-all.sh
```

**Check status:**
```bash
./status.sh
```

**View logs:**
```bash
# All services
./logs.sh all

# Specific service
./logs.sh notification
./logs.sh customer
./logs.sh email
./logs.sh frontend
```

## Service URLs

Once started, access:

- **Frontend**: http://localhost:3000
- **Notification Service API**: http://localhost:8002/docs
- **Customer Service API**: http://localhost:8001/docs
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **Wiremock**: http://localhost:8089

## Features

### Notification Management
- Create email notifications with subject, body, and customer IDs
- Track notification status: PENDING → PROCESSING → COMPLETED/FAILED
- View all notifications with real-time status updates

### Retry Mechanism
- Automatic retry with dead-letter queue (DLQ)
- Up to 3 retry attempts with 1-minute delays
- Failed messages don't block the queue
- 5-minute timeout for stuck messages

### Message Flow
```
1. Frontend → Notification Service (Create notification)
2. Notification Service → RabbitMQ (Publish to email.send queue)
3. Email Sender → RabbitMQ (Consume and process)
4. Email Sender → RabbitMQ (Publish status to email.status queue)
5. Notification Service → RabbitMQ (Consume status update)
6. Frontend → Notification Service (Poll for updates)
```

## Development

### Running Individual Services

If you need to run services individually:

```bash
# Notification service
cd notification-service
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Customer service
cd customer-service
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Email sender
cd email-sender
source ../.venv/bin/activate
python app/main.py

# Frontend
cd frontend
npm run dev
```

### Logs Location

All logs are stored in `./logs/` directory:
- `notification-service.log`
- `customer-service.log`
- `email-sender.log`
- `frontend.log`

## Troubleshooting

**Services won't start:**
- Check if ports are already in use: `lsof -i :3000,8001,8002`
- Check Docker is running: `docker ps`
- Check logs: `./logs.sh all`

**Database issues:**
- Reset database: `docker-compose down -v && docker-compose up -d`

**RabbitMQ issues:**
- Access management UI: http://localhost:15672
- Check queues: `email.send`, `email.status`, `email.send.dlq`

**Frontend can't connect to backend:**
- Check backend is running: `./status.sh`
- Verify proxy config in `frontend/vite.config.ts` points to port 8002

## Technology Stack

**Backend:**
- FastAPI
- SQLAlchemy
- PostgreSQL
- RabbitMQ (aio-pika)
- Pydantic

**Frontend:**
- React 18
- TypeScript
- Vite
- Axios

**Infrastructure:**
- Docker & Docker Compose
- Wiremock for mocking external APIs
