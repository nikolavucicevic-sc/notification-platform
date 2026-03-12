# Docker Setup Guide

This document explains the Docker setup for the Notification Platform.

## Docker Architecture

All services are containerized and orchestrated with Docker Compose:

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network (bridge)                   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │ RabbitMQ │  │ Wiremock │  │ Frontend │   │
│  │  :5432   │  │ :5672    │  │  :8089   │  │   :80    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│  ┌────┴─────────────┴──────────────┴─────────────┘          │
│  │                                                           │
│  ├──────────────┬──────────────┬──────────────┐            │
│  │              │              │              │            │
│  │ Notification │  Customer   │    Email     │            │
│  │   Service    │   Service   │   Sender     │            │
│  │    :8002     │    :8001    │              │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Services

### Infrastructure Services

1. **PostgreSQL** (postgres:15)
   - Port: 5432
   - Database: notification_platform
   - User: admin / admin
   - Persistent volume for data

2. **RabbitMQ** (rabbitmq:3-management)
   - Messaging: 5672
   - Management UI: 15672
   - User: admin / admin
   - Persistent volume for queue data

3. **Wiremock** (wiremock/wiremock:latest)
   - Port: 8089
   - Mocks external email API

### Application Services

4. **notification-service**
   - Port: 8002
   - FastAPI REST API
   - Manages notifications and status updates
   - Consumes from: email.status queue
   - Publishes to: email.send queue

5. **customer-service**
   - Port: 8001
   - FastAPI REST API
   - Manages customer data

6. **email-sender**
   - No exposed port (background worker)
   - Consumes from: email.send queue, email.send.dlq
   - Publishes to: email.status queue
   - Includes retry mechanism with DLQ

7. **frontend**
   - Port: 3000 (mapped to container port 80)
   - React + TypeScript SPA
   - Nginx server with API proxy

## Dockerfiles

### Python Services (notification-service, customer-service, email-sender)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD [...]
```

### Frontend (Multi-stage build)

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
```

## Features

### Health Checks

All infrastructure services have health checks:
- PostgreSQL: `pg_isready`
- RabbitMQ: `rabbitmq-diagnostics ping`
- Wiremock: HTTP health endpoint

Application services depend on healthy infrastructure before starting.

### Service Dependencies

```yaml
notification-service:
  depends_on:
    postgres: service_healthy
    rabbitmq: service_healthy

email-sender:
  depends_on:
    rabbitmq: service_healthy
    wiremock: service_healthy

frontend:
  depends_on:
    - notification-service
```

### Restart Policy

All application services have `restart: unless-stopped` to ensure high availability.

### Networking

All services communicate on a custom bridge network (`notification-network`), enabling:
- Service discovery by name (e.g., `http://notification-service:8002`)
- Isolated network communication
- Better security

### Volumes

Persistent volumes for data:
- `postgres_data` - Database storage
- `rabbitmq_data` - Message queue data

## Environment Variables

Services are configured via environment variables in docker-compose.yml:

```yaml
notification-service:
  environment:
    DATABASE_URL: postgresql://admin:admin@postgres:5432/notification_platform
    RABBITMQ_URL: amqp://admin:admin@rabbitmq:5672/
    RABBITMQ_EMAIL_QUEUE: email.send
    RABBITMQ_STATUS_QUEUE: email.status
```

## Usage

### Start all services
```bash
docker-compose up -d
# or
./start-docker.sh
```

### View logs
```bash
docker-compose logs -f                       # All services
docker-compose logs -f notification-service  # Specific service
```

### Stop all services
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose up --build -d
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
```

### Access services
- Frontend: http://localhost:3000
- Notification API: http://localhost:8002/docs
- Customer API: http://localhost:8001/docs
- RabbitMQ Management: http://localhost:15672
- PostgreSQL: localhost:5432

## Development Workflow

### Making Code Changes

1. **Backend (Python) services:**
   ```bash
   # Edit code in notification-service/app/, customer-service/app/, or email-sender/app/
   docker-compose up --build -d notification-service
   # or rebuild specific service
   ```

2. **Frontend:**
   ```bash
   # Edit code in frontend/src/
   docker-compose up --build -d frontend
   ```

### Debugging

View logs for a specific service:
```bash
docker-compose logs -f notification-service
```

Access a running container:
```bash
docker exec -it notification-service /bin/bash
```

Check service health:
```bash
docker-compose ps
```

### Local Development vs Docker

You can mix modes:
- Run infrastructure in Docker: `docker-compose up -d postgres rabbitmq wiremock`
- Run application services locally: `./start-all.sh`

This is useful for debugging with breakpoints.

## Troubleshooting

### Service won't start
```bash
docker-compose logs service-name
docker-compose ps
```

### Port conflicts
Ensure ports 3000, 5432, 5672, 8001, 8002, 8089, 15672 are available.

### Database connection issues
Wait for PostgreSQL health check:
```bash
docker-compose logs postgres
```

### RabbitMQ connection issues
Wait for RabbitMQ health check:
```bash
docker-compose logs rabbitmq
```

### Fresh start
```bash
docker-compose down -v
docker-compose up --build -d
```
