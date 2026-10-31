# Portfolio & resume guidance (honest)

## One-liner
Multi-tenant price intelligence platform: observation history, anomaly detection, hybrid matching, tool-calling market analyst, Celery scraping, Redis rate limits/cache, Stripe billing, Docker + CI.

## Resume bullets (only after you can demo them)

- Built a multi-tenant pricing intelligence API (FastAPI, PostgreSQL) with ownership isolation, JWT auth, and Redis rate limiting.
- Implemented async scraping workers (Celery/Redis) with cooldowns, retries, job audit rows, and append-only price observations.
- Shipped hybrid product matching (fuzzy + variant penalties) and statistical anomaly detection (z-score, IQR, MAD).
- Added an evidence-grounded market analyst using authorized tool calling (no unrestricted DB access for the model).
- Containerized services and automated tests/CI (pytest, Alembic on Postgres, frontend typecheck/build).

## Interview risks to avoid

| Claim | Safer framing |
|-------|----------------|
| “Scrapes all major retailers” | “Adapter pattern + permitted practice source; production needs official APIs” |
| “AI predicts prices accurately” | “Experimental baseline forecast with explicit uncertainty” |
| “Fully deployed at scale” | “Compose-ready; measure load with load_test script” |

## Artifacts to keep in GitHub

- `docs/SPRINT0_TECHNICAL_AUDIT.md` (if present) or PROJECT_STATUS  
- `docs/DEMO_SCRIPT.md`  
- `docs/SECURITY_CONTROLS.md`  
- `docs/decisions/` ADRs  
- Phase batch notes under `docs/PHASES_*`  
