# Phases 0–4 batch (2026-10-29)

## What was delivered

### Phase 0 — Audit
- `docs/PROJECT_AUDIT.md` — component status, evidence, next actions

### Phase 2 — Schema / history foundation
- Alembic revision `a1b2c3d4e5f6_price_observations_and_indexes.py`
  - `sources` table (if missing)
  - `price_observations` table (if missing)
  - Index on `(listing_id, scraped_at DESC)` for history queries

### Phase 3 — Ingestion
- Registered `books_toscrape` (and alias `books`) in `ADAPTER_REGISTRY`
- Compat wrapper maps BooksToScrapeAdapter fetch/parse → scrape_service dict
- Sync price history API:
  - `GET /api/products/{product_id}/prices?limit=100`
  - `POST /api/listings/{listing_id}/scrape` (manual trigger, rate-limited)
- Mounted `prices` router on main app (v0.2.0)

### Phase 4 — Rate limiting
- `backend/app/core/rate_limit.py` — Redis fixed-window limiter
- Policies:
  - Login: 5 / min / IP
  - Register: 3 / min / IP
  - Product reads: 120 / min / user+IP
  - Product writes: 30 / min / user+IP
  - Scrape trigger: 10 / min / user+IP
- HTTP 429 + `Retry-After` + structured error body
- Fail-open if Redis is down (documented)

## How to run (local)

```bash
# From repo root
cp .env.example .env
# Set SECRET_KEY, DATABASE_URL, REDIS_URL as needed

docker compose up --build   # or run services separately

# Backend only
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Celery (optional for background scrape)
celery -A app.workers.celery_app worker --loglevel=info

# Frontend
cd frontend
npm install && npm run dev
```

## Quick API checks

```bash
# Register
curl -s -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@priceloop.ai","password":"Secret123!"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@priceloop.ai","password":"Secret123!"}' | jq -r .access_token)

# Create product with listing (demo or books_toscrape URL)
curl -s -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Demo Book","listings":[{"source":"books_toscrape","url":"https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"}]}'

# Trigger scrape (use listing id from create response)
curl -s -X POST http://localhost:8000/api/listings/<LISTING_ID>/scrape \
  -H "Authorization: Bearer $TOKEN"

# History
curl -s http://localhost:8000/api/products/<PRODUCT_ID>/prices \
  -H "Authorization: Bearer $TOKEN"
```

## Tests

```bash
cd backend && pip install -r requirements-dev.txt && pytest tests/ -v
PYTHONPATH=. pytest scraper/tests/ -v
```

## Not in this batch
- Full search UI + charts wired to new history endpoint
- Production load test of rate limits
- Live marketplace adapters beyond books.toscrape
- Alert evaluation / AI analyst
