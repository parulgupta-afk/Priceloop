# Phases 12–15 batch

## Phase 12 — Authz hardening
- Cross-user product isolation test
- Existing JWT + ownership checks verified via tests

## Phase 13 — Testing & CI
- `tests/test_intelligence.py` — analytics empty path, MAD/z-score units, isolation, alerts CRUD, insights shape
- Existing CI: backend pytest, scraper pytest, Alembic up/down on Postgres, frontend tsc + build

## Phase 14 — Observability
- `RequestContextMiddleware` — X-Request-ID, structured access log
- `GET /metrics` — uptime + counters

## Phase 15 — Deployment
- `docs/DEPLOYMENT.md` production checklist
- Compose prod path unchanged; document rollback + health

API version **0.5.0**
