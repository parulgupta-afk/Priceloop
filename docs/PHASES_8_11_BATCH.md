# Phases 8–11 batch

## Phase 8 — Anomaly detection
- `GET /api/products/{id}/anomalies?days=60`
- Methods: z-score, IQR, % rolling deviation, **MAD**
- Multi-method agreement → higher confidence
- Explicit note: anomaly ≠ proven deal

## Phase 9 — Product matching
- `GET /api/products/{id}/matches?min_score=0.75`
- Title + brand + model weighted score with explanation

## Phase 10 — AI market analyst (grounded)
- `GET /api/products/{id}/insights?days=30`
- Stats computed in code; rule-based summary; no invented causes
- Structured: summary, observations, possible_explanations, confidence, limitations

## Phase 11 — Alerts
- `POST /api/alerts` — create (PRICE_DROP_PCT, PRICE_INCREASE_PCT, ANOMALY, OUT_OF_STOCK, ...)
- `GET /api/alerts` — list
- `DELETE /api/alerts/{id}`
- `POST /api/alerts/evaluate` — run evaluation for current user

API version **0.4.0**
