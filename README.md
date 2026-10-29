# PriceLoop

Production-minded **price intelligence** platform for SDE portfolio demos.

Track products, store **historical price observations**, run analytics and anomaly detection, set alerts, and get **evidence-grounded** insights — with rate limiting, Redis cache, Celery workers, Stripe billing, Docker, and CI.

See `docs/PROJECT_STATUS.md` and phase docs under `docs/` for an honest implemented vs planned split.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, JWT, Stripe
- **Scraper:** httpx, BeautifulSoup, adapter interface (`demo`, `books.toscrape`)
- **Frontend:** React, TypeScript, Vite, Tailwind, recharts
- **Ops:** Docker Compose, GitHub Actions, structured access logs, `/health/*`, `/metrics`

## Core capabilities (API v0.6)

| Area | Endpoints / behavior |
|------|----------------------|
| Auth | Register / login / me (rate-limited) |
| Products | CRUD + `?q=` search, ownership isolation |
| Prices | `GET /api/products/{id}/prices`, manual scrape |
| Analytics | `GET /api/products/{id}/analytics` |
| Anomalies | z-score, IQR, %, MAD |
| Matching | title/brand/model score + explanation |
| Insights | grounded summary (no invented causes) |
| Alerts | create / list / delete / evaluate |
| Billing | Stripe Checkout + webhooks |
| Jobs | Celery scrape + cooldown + beat schedule |
| Cache | Redis TTLs on prices/analytics |
| Ops | live/ready health, metrics, request IDs |

## Quick start

```bash
cp .env.example .env
# set SECRET_KEY, DATABASE_URL, REDIS_URL

docker compose up --build
# or locally:
cd backend && pip install -r requirements.txt && alembic upgrade head
uvicorn app.main:app --reload --port 8000
celery -A app.workers.celery_app worker --loglevel=info

cd frontend && npm install && npm run dev
```

### Demo seed (real books.toscrape URLs only)

No fake Sony/Amazon prices. Catalog points at [books.toscrape.com](https://books.toscrape.com)
(explicitly scrapable). Seed **fetches live prices** into `price_observations`.

```bash
cd backend && python -m scripts.seed_demo_sync
# login: demo@priceloop.ai / Demo123!
# if scrape fails offline: POST /api/listings/{id}/scrape later
```

### Load test (measure, do not invent numbers)

```bash
cd backend && python -m scripts.load_test --base http://localhost:8000 --users 5 --requests 30
```

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/PROJECT_AUDIT.md` | Component status |
| `docs/DEPLOYMENT.md` | Production checklist |
| `docs/ARCHITECTURE.md` | Layering |
| `docs/decisions/` | ADRs |
| `docs/PHASES_*_BATCH.md` | What each roadmap batch shipped |

## Tests

```bash
cd backend && pip install -r requirements-dev.txt && pytest tests/ -v
PYTHONPATH=. pytest scraper/tests/ -v
```

## Security notes

- Production refuses weak `SECRET_KEY`, SQLite, wildcard CORS
- Stripe webhook signatures verified
- Rate limits on auth and expensive routes
- Errors do not expose stack traces to clients

## License

MIT
