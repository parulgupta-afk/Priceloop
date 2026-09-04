# Phases 7 – 9 Summary

## Phase 7 — Competitive Analytics Polish (Completed)

What was added:
- Richer competitive snapshot already present from Phase 4 is now joined into a single **intelligence summary** endpoint.
- New endpoint:
  - `GET /api/v1/products/{id}/summary?days=30`
    → returns analytics + competitive position in one payload (perfect for a dashboard card).

This makes the backend “frontend-ready” for a product detail page without multiple round-trips.

## Phase 8 — Anomaly Detection (Completed)

What was added:
- `anomaly_service.py` with three statistical detectors:
  - Z-score (threshold 2.5)
  - IQR (1.5 × inter-quartile range)
  - Percentage deviation from rolling mean (≥ 15%)
- Unified anomaly objects with:
  - direction (SPIKE / DROP)
  - severity (HIGH if ≥ 2 detectors agree, else MEDIUM)
  - change % and supporting observation IDs
- Endpoint:
  - `GET /api/v1/products/{id}/anomalies?days=60`

Design notes:
- Requires at least 5 observations.
- Multiple detectors reduce false positives.
- Fully deterministic – no ML model needed yet.

## Phase 9 — Price Forecasting Foundation (Completed)

What was added:
- `forecast_service.py` using:
  - Moving Average
  - Exponential Smoothing
  - Simple linear trend
- Blended point forecast + uncertainty band derived from recent volatility
- Direction label (Likely Up / Down / Stable)
- Confidence score (heuristic based on data volume + volatility)
- Endpoint:
  - `GET /api/v1/products/{id}/forecast?horizon_days=7&history_days=60`

Important:
- Always returns a confidence / range – never a single “magic” number.
- Explicit note that it is a probabilistic estimate only.

---

## New API surface (this batch)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/products/{id}/summary` | Dashboard-ready combined view |
| GET | `/api/v1/products/{id}/anomalies` | Statistical price anomalies |
| GET | `/api/v1/products/{id}/forecast` | Short-term forecast + band + confidence |

---

## What you can demo now

1. Scrape a product several times (or seed multiple observations).
2. Call `/analytics` and `/summary` → show price intelligence numbers.
3. Call `/anomalies` → highlight spikes/drops.
4. Call `/forecast` → show expected range and direction with confidence.

This turns the project into a genuine **price intelligence engine**, not just a scraper + database.
