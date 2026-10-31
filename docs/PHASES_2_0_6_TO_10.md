# PriceLoop 2.0 — Phases 6–10

## Phase 6 — Forecasting
- `GET /api/products/{id}/forecast?horizon_days=7`
- ES + trend vs last/MA baselines; always `label: experimental`

## Phase 7 — Alert intelligence
- `POST /api/alerts/evaluate-deduped` — 6h dedupe window

## Phase 8 — Frontend
- API base default `http://localhost:8000/api` (not `/api/v1`)
- `mockData` empty defaults
- On login, load products via `listProducts` + mapper
- `api/intelligence.ts` for summary/forecast/analyst

## Phase 9 — Security
- `docs/SECURITY_CONTROLS.md`

## Phase 10 — Tests
- `test_forecast_and_notifications.py`
- Existing CI workflow retained

API remains **1.0.0** (feature batch on 2.0 track).
