# Phases 10 – 12 Summary

## Phase 10 — AI Insight Engine (Completed)

- `insight_service.py`
  - Builds **structured context** from analytics + competitors + anomalies + forecast
  - Generates a plain-language summary + recommendation
  - Uses a deterministic template when no LLM API key is configured (demos always work)
  - Ready for real LLM injection later (context-only → no price hallucination)
- Endpoint: `GET /api/v1/products/{id}/insights`

## Phase 11 — Natural Language Query (Completed foundation)

- `nl_query_service.py`
  - Simple intent detection (forecast / anomaly / competitive / insight / analytics)
  - Maps questions onto existing deterministic services
  - No free-form SQL – safe and auditable
- Endpoint: `POST /api/v1/ai/query`
  ```json
  { "question": "Why did the price drop?", "product_id": "..." }
  ```

## Phase 12 — Smart Alerts (Completed foundation)

- Models: `Alert`, `AlertEvent`, `AIInsight`
- Rule types: PRICE_DROP_PCT, PRICE_INCREASE_PCT, ANOMALY, etc.
- `alert_service.py` evaluates rules against latest analytics/anomalies
- Endpoints:
  - `GET  /api/v1/alerts`
  - `POST /api/v1/alerts`
  - `POST /api/v1/products/{id}/alerts/evaluate`

## Frontend (Scaffolded)

Minimal Next.js 14 App Router UI:
- Dashboard home
- Login / Register (talks to backend JWT)
- Products list + create

Enough to demonstrate the full stack end-to-end.
