# PriceLoop — Project Status (deployment audit)

## IMPLEMENTED

| Area | Notes |
|------|--------|
| Auth | Register, login (JSON), JWT access tokens, `/api/auth/me` |
| Products | CRUD-style list/create/get with ownership |
| Billing | Stripe checkout hooks (requires real Stripe keys) |
| Health | `/health`, `/health/live`, `/health/ready` (Postgres + Redis) |
| DB | SQLAlchemy sync + Alembic initial migration |
| Docker prod | postgres, redis, migrate, backend, worker, frontend (Nginx) |
| Docker image | Repo-root context copies `backend/` + `scraper/` |
| Celery | Worker boots; `scrape.listing` / `scrape.all_active` registered (sync DB) |
| Scraper | Adapter registry + demo adapter + normalization helpers |
| Frontend | React + Vite production build served by Nginx; `/api` proxied |
| CI | GitHub Actions: backend tests, scraper tests, Alembic up/down, frontend tsc+build |
| Security | Production rejects weak `SECRET_KEY`; bcrypt passwords; ownership on products |

## PLANNED / PARTIAL

| Area | Notes |
|------|--------|
| Full analytics/anomaly/forecast API surface | Services exist under `app/services/`; not all mounted on `main.py` |
| Live Amazon/Flipkart adapters | Not claimed; demo adapter only |
| pgvector embeddings pipeline | Schema/docs mention; not required for current models |
| Prometheus/Grafana | Not implemented |
| Refresh tokens | Access JWT only in current security module |
| Deep learning forecasting | Statistical helpers only |

## DEPLOYMENT READINESS

- Compose production file is structurally complete.
- **Runtime Docker verification depends on host Docker + a filled production `.env`.**
- CI exists on `main`; success depends on GitHub Actions runners (not guaranteed offline).
