# PriceLoop 2.0 — Phases 1–5 batch (2026-10-31)

Built on Sprint 0 audit of GitHub main @ ~db42d48.

## Phase 1 — Backend / DB
- Single mounted intelligence surface remains source of truth (sync Session).
- Orphan `api/analytics.py` and `api/ai.py` marked **DEPRECATED** (async drift).
- Alembic `b2c3d4e5f607` adds `scrape_jobs` for job audit.
- API version **1.0.0**.

## Phase 2 — Scraping & data engineering
- `scrape_service` records RUNNING/SUCCESS/FAILED jobs with duration_ms.
- Retries via `retry_with_backoff` when available.
- `GET /api/scrape-jobs` — user-scoped job history.

## Phase 3 — Matching engine v2
- Hybrid fuzzy + SKU/GTIN bonus.
- **Variant penalties** for storage/color mismatch (128GB vs 256GB).
- `review_required` flag for mid-confidence matches.

## Phase 4 — Analytics
- Existing MAD/z/IQR/% retained.
- `GET /api/products/{id}/summary` — analytics + anomalies + insight card payload.

## Phase 5 — AI Market Analyst
- `POST /api/ai/query` with **authorized tools only** (list products, analytics, anomalies, matches, insights, alerts).
- Deterministic planner (works without LLM keys); evidence + tool_trace returned.
- No unrestricted SQL for the model.

## Quick test
```bash
TOKEN=...
curl -s -X POST http://localhost:8000/api/ai/query \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"query":"Which products had unusual price moves?"}'
```
