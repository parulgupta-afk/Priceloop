# Phases 16–18 batch

## Phase 16 — Distributed resilience
- `app/core/resilience.py` — retry with exponential backoff + jitter, circuit breaker
- Use for outbound HTTP (scrapers / LLM); not for local DB sessions

## Phase 17 — Load testing
- `python -m scripts.load_test --users 5 --requests 30`
- Prints measured p50/p95/p99 and error rate — paste into docs; never invent

## Phase 18 — Portfolio polish
- README rewritten to match real capabilities
- ADRs under `docs/decisions/`
- Sync demo seed: `python -m scripts.seed_demo_sync`

API version **0.6.0**
