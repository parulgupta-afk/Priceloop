# Phases 4 – 6 Summary

## Phase 4 — Price History & Basic Analytics (Completed)

What was added:
- `analytics_service.py`
  - Current / previous / min / max / average / median price
  - Percentage change over the window
  - Last observation change
  - Simple volatility (coefficient of variation)
- Competitive snapshot across all listings of a product
  - Market median, average, lowest, highest
  - Rough “Premium / Competitive / In line” position label
- New API endpoints:
  - `GET /api/v1/products/{id}/analytics?days=30`
  - `GET /api/v1/products/{id}/competitors`

These calculations are 100% deterministic and based only on stored `PriceObservation` rows.

## Phase 5 — Background Processing & Scheduling (Completed foundation)

What was added:
- `scrape.all_active` Celery task that finds every active listing and enqueues individual `scrape.listing` jobs
- Celery Beat schedule skeleton (`scheduler.py`) – hourly scrape of all active listings
- Proper include of scheduler module in the Celery app

How to run later:
```bash
# Worker
celery -A app.workers.celery_app worker --loglevel=info

# Beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

This gives you a real distributed job story for the portfolio.

## Phase 6 — Product Matching Foundation (Started & usable)

What was added:
- `ProductMatch` model (confidence, method, reviewed, is_confirmed)
- `matching_service.py`
  - Text normalization
  - Brand / model extraction heuristics
  - Fuzzy title + brand + model scoring
  - Confidence levels: HIGH (≥0.90), MEDIUM (≥0.75), LOW
- API endpoints:
  - `GET  /api/v1/products/{id}/matches` → ranked potential matches
  - `POST /api/v1/products/{id}/matches/{other_id}` → manually confirm a match

Matching is intentionally conservative and always returns a confidence score. Low-confidence matches stay in a review path.

Next improvements for matching (future):
- sentence-transformers embeddings + pgvector
- Attribute-level comparison (color, storage, size)
- Cross-user / catalog-wide matching

---

## What you can demo right now

1. Create two similar products (e.g. “Sony WH-1000XM5” and “Sony WH1000XM5 Wireless Headphones”)
2. Call `/matches` → see confidence score
3. Confirm a match
4. Scrape listings → call `/analytics` and `/competitors`
5. Show the numbers on a dashboard later

This batch turns the project from “CRUD + one scrape” into a real **price intelligence** foundation.
