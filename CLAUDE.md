# Bemby Notify — Claude Code Instructions

## Project Overview

Multi-tenant SaaS notification platform ("Bemby Notify"). Tenants sign up, get API keys, and use the platform to send emails and SMS to their customers. Built with FastAPI microservices + React frontend on a single EC2 instance.

**Production:** `http://3.74.152.191:3000`
**GitHub:** `nikolavucicevic-sc/notification-platform`

---

## Architecture

| Service | Port | Description |
|---|---|---|
| `notification-service` | 8002 | Core API — auth, tenants, notifications, billing |
| `customer-service` | 8001 | Tenant customer CRUD |
| `scheduler-service` | 8003 | Scheduled notification jobs |
| `template-service` | 8004 | Email/SMS template management |
| `email-sender` | — | Redis consumer → Brevo API |
| `sms-sender` | — | Redis consumer → SMS API |
| `frontend` | 3000 | React + Nginx reverse proxy |
| `postgres` | 5432 | Shared DB (`notification_platform`) |
| `redis` | 6379 | Async job queue |
| `prometheus` | 9090 | Metrics scraping |
| `grafana` | 3001 | Dashboards |
| `jaeger` | 16686 | Distributed tracing |
| `locust` | 8090 (host) → 8089 | Load testing |

All backend services share the same PostgreSQL database. Alembic migrations are managed in `notification-service/alembic/`.

---

## Key Conventions

### Authentication
- JWT tokens issued by `notification-service` using `SECRET_KEY` env var
- All services that need auth decode the same JWT with the same `SECRET_KEY`
- `customer-service` decodes JWT and queries `users` table via raw SQL (no ORM FK to notification-service models)
- Auth returns `(tenant_id, role)` tuple; roles: `SUPER_ADMIN`, `ADMIN`, `VIEWER`

### Tenant Isolation
- Every data model has `tenant_id` column
- All queries filter by `tenant_id` from the JWT
- `SUPER_ADMIN` can see all tenants' data
- `customer-service` enforces isolation in `app/routers/customers.py`

### SQLAlchemy FK Rule
**Do NOT add `ForeignKey(...)` constraints to SQLAlchemy models** that reference tables owned by other services (e.g., `tenants.id` from `customer-service`). Use a comment instead:
```python
tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # FK to tenants.id enforced by migration
```
This prevents `NoReferencedTableError` in tests where only one service's tables exist.

### Database Migrations
- All migrations live in `notification-service/alembic/versions/`
- Naming: `YYYYMMDD_NNNN-description.py`
- Run via `start.sh` before the service starts in production

### Email Sending
- Brevo API (`email-sender/app/services/email_client.py`)
- Per-tenant branding: `display_name`, `reply_to_email`, `email_alias`
- Email alias: if `email_alias` + `BREVO_SENDING_DOMAIN` set → sends as `alias@domain`
- Falls back to global `BREVO_FROM_EMAIL` if not configured
- Tenant branding fetched from `notification-service` internal endpoint: `GET /tenants/{id}/branding`

### Redis Queue
- `email-sender` and `sms-sender` are Redis consumers (not HTTP services)
- No health port for these — they just consume queue items

### Frontend
- React + TypeScript in `frontend/src/`
- Nginx reverse proxy routes `/api/*` to backend services
- Polling state (interval, enabled) persisted in `localStorage` — keys: `notif_poll_seconds`, `notif_polling_enabled`

---

## Environment Variables

Required in `.env` or set in shell before `docker compose up`:

```bash
SECRET_KEY=<strong-random-key>          # Shared across all services
BREVO_API_KEY=<brevo-api-key>
BREVO_FROM_EMAIL=sender@yourdomain.com
BREVO_SENDING_DOMAIN=yourdomain.com     # For per-tenant aliases
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_BUSINESS=price_...
```

---

## Development

### Run locally (dev — includes wiremock, locust, jaeger)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Run in production mode (no dev tools)
```bash
docker compose up -d
```

### Run tests
```bash
# All services
./run-tests.sh

# Single service (uses requirements-test.txt)
cd customer-service && pytest -m unit -v
cd notification-service && pytest -m unit -v
cd scheduler-service && pytest -m unit -v
```

### Check service health
```bash
./check-services.sh
```

### Deploy to EC2 (auto via CI/CD on push to main)
```bash
git push origin main
```

---

## CI/CD

- `.github/workflows/ci.yml`
- Runs `pytest -m unit -v` per service on every push/PR
- Deploys to EC2 on push to `main` via `appleboy/ssh-action`
- EC2 secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY` in GitHub repo settings
- **Docker builds are sequential** (one service at a time) — EC2 has only 1GB RAM, parallel builds OOM
- Uses `DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0` — EC2 doesn't have buildx

---

## Billing (Stripe)

- Plans: `FREE` (1k email / 500 SMS/mo), `PRO` (50k / 10k), `BUSINESS` (unlimited)
- Checkout: `POST /billing/create-checkout`
- Webhooks: `POST /billing/webhook`
- Router: `notification-service/app/routers/billing.py`

---

## Nginx Routing Rules

- Use prefix-match (`location /api/tenants`) not exact/trailing-slash (`location /api/tenants/`)
- All backend paths proxied without double `/api/` prefix
- Billing endpoint: `location /api/billing`

---

## Skills

Use `/deploy` to deploy, `/test` to run tests, `/health` to check services.
