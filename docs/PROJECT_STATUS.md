# Project Status

Last updated: alongside the deployment-readiness pass (Docker fix, Alembic
migrations, health checks, CI, real test suite).

This file exists to keep one honest answer to "does X actually work?" in
one place, instead of scattered across commit messages.

## Implemented and tested

| Area | What's real | Verified by |
|---|---|---|
| Authentication | Register, login, JWT issuance/validation, password hashing (bcrypt via passlib), `/api/auth/me` | `backend/tests/test_auth.py` (12 tests) |
| Products | Create/list/get, nested listings, per-user ownership isolation | `backend/tests/test_products.py` (8 tests) |
| Billing | Stripe Checkout session creation, webhook handling (`checkout.session.completed`, `subscription.updated`, `subscription.deleted`), Subscription model | `backend/tests/test_billing.py` (6 tests, webhook logic tested with mocked signature verification) |
| Health checks | `/health/live` (process up), `/health/ready` (DB + Redis reachability) | `backend/tests/test_health.py` (4 tests) |
| Scraper | `books.toscrape.com` adapter, price/availability normalization (handles US/EU/Indian currency formats) | `scraper/tests/` (11 tests) |
| Database migrations | Alembic initialized, initial schema migration generated and verified (upgrade + downgrade round-trip tested) | Manually run against SQLite in this environment; **not yet run against real Postgres** (no Postgres available in the dev sandbox this was built in) |
| Docker | Production-safe Dockerfile (repo-root build context so `scraper/` is actually included, non-root user, no `--reload`, healthcheck), separate dev/prod compose files | Verified via simulated file-layout import test (not an actual `docker build`, since Docker isn't available in this environment) |
| CI | GitHub Actions workflow: backend tests + Alembic migration check against real Postgres/Redis service containers, frontend type-check + build | YAML syntax validated; **not yet run on GitHub's actual runners** (that only happens once pushed) |
| Frontend | Full dashboard UI (from the AI Studio-generated app), real login/signup wired to the backend, real Stripe checkout redirect | `tsc --noEmit` + `vite build` both clean |

## Explicitly NOT implemented (do not claim these in interviews/demos)

These were referenced in an earlier planning document but no code for them
exists in this repository. Writing tests for them was skipped rather than
faked, per "don't write superficial tests just to increase coverage."

- **Analytics** (min/max/average/median/volatility/price-position) — no code
- **Cross-marketplace product matching** (fuzzy/embedding-based) — the
  scraper's registry pattern supports adding matching later, but no
  matching logic exists yet
- **Anomaly detection** (z-score, IQR, deviation-based) — no code
- **Price forecasting** (moving average, exponential smoothing, confidence
  intervals) — no code
- **Alerts** (rule engine, triggered/non-triggered evaluation) — no code
- **Refresh tokens** — `REFRESH_TOKEN_EXPIRE_DAYS` exists as a config value
  for when this is built, but there is no refresh-token endpoint or logic
- **RBAC beyond a stored role field** — `User.role` exists
  (`USER`/`ADMIN`/`ANALYST`) but no endpoint currently checks it; anyone
  authenticated can do anything a `USER` can do
- **pgvector, embeddings** — not used anywhere
- **LLM-generated insights** (Phase 15 in the roadmap) — `LLM_PROVIDER`,
  `OPENAI_API_KEY` etc. exist as reserved config, but no code calls an LLM
- **Email notifications** (Phase 18) — SMTP config exists as reserved
  settings, no code sends email
- **Screenshot verification / object storage** (Phase 21) — S3 config
  exists as reserved settings, no code uploads anything
- **Real scraping of Amazon/Walmart/etc.** — only `books.toscrape.com` (a
  site built for scraping practice) is implemented; no adapter exists for
  any real e-commerce marketplace yet

## Known limitations (real, not blocking, worth fixing eventually)

- No rate limiting on `/api/auth/login` (brute-force risk at scale)
- Alembic migration has only been tested against SQLite in this
  environment, not a real Postgres instance
- Docker build has been verified by simulating the file layout and import
  paths, not by an actual `docker build` (Docker isn't available in the
  environment this was built in)
- CI workflow syntax is valid but has never actually executed on GitHub's
  runners
- Several deprecation warnings surfaced during testing (FastAPI's
  `on_event`, Pydantic's class-based `Config`, SQLAlchemy's
  `datetime.utcnow()` column defaults) -- none break anything today, but
  will need addressing before a future dependency upgrade removes them
