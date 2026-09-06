# PriceLoop — Project Status

## IMPLEMENTED

- Auth: register, login (JSON JWT), `/api/auth/me`, bcrypt passwords
- Products: create/list/get with ownership checks
- Billing: Stripe checkout hooks (optional keys)
- Health: `/health`, `/health/live`, `/health/ready`
- SQLAlchemy + Alembic initial schema
- Celery worker with sync scrape tasks
- Scraper package + demo adapter + normalization
- React/Vite frontend + Nginx production image
- Docker Compose production stack (postgres, redis, migrate, backend, worker, frontend)
- CI: backend tests, scraper tests, Alembic, frontend tsc + build
- Portable JSON columns (Postgres JSONB / SQLite JSON for tests)

## OPTIONAL / FUTURE

- Full analytics/anomaly/forecast HTTP routes mounted on main
- Live marketplace adapters (Amazon etc.)
- pgvector embedding pipeline
- Refresh tokens
- Prometheus/Grafana

## TEST DEPENDENCIES

Install test tooling with:

```bash
pip install -r backend/requirements-dev.txt
```

Production images use `requirements.txt` only (no pytest).
