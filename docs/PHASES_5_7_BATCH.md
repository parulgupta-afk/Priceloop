# Phases 5–7 batch (2026-10-29)

Builds on Phases 0–4 (audit, schema, ingestion, rate limits).

## Phase 5 — Product experience (API)

- Product list supports `?q=` name search, `skip`, `limit`
- `GET /api/products/{id}/prices` — history (cached)
- `GET /api/products/{id}/analytics?days=30` — current/previous, % change, min/max/avg/median, volatility
- Manual scrape still at `POST /api/listings/{id}/scrape`

## Phase 6 — Background processing

- Celery tasks with **5-minute cooldown** (skip if recently scraped — reduces duplicate observations)
- Bounded retries with backoff on `scrape.listing`
- Beat schedule loads via `scheduler.py` (hourly `scrape.all_active`)
- Cache invalidation after successful scrape

## Phase 7 — Caching

- Redis cache-aside: prices (60s), analytics (90s)
- Fail-open if Redis down
- Invalidation on scrape

## Run

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

## API examples

```bash
# Search
curl -s "http://localhost:8000/api/products/?q=laptop" -H "Authorization: Bearer $TOKEN"

# Analytics
curl -s "http://localhost:8000/api/products/$PID/analytics?days=30" -H "Authorization: Bearer $TOKEN"

# History
curl -s "http://localhost:8000/api/products/$PID/prices?limit=50" -H "Authorization: Bearer $TOKEN"
```

API version: **0.3.0**
