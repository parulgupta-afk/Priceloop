# Priceloop

A price-tracking platform: register/log in, track a product across
marketplaces, and see its price history and competitor comparison on a
dashboard. Billing is wired to real Stripe Checkout. See
`docs/PROJECT_STATUS.md` for a precise, honest breakdown of what's
implemented vs. planned -- this README summarizes it, that file is the
source of truth.

## 1. Project overview

Priceloop currently does three real things: authenticate users, let a
user track a product (with one or more marketplace listings) they own,
and take a real Stripe subscription payment for a paid plan. A scraper
skeleton (one working adapter, for a scraping-practice site) and a full
dashboard UI exist, but analytics, cross-marketplace product matching,
anomaly detection, forecasting, and alerts are **not yet implemented** --
see Known Limitations below.

## 2. Architecture

```
React frontend (Vite)
        |
        v  (JWT bearer auth)
   FastAPI backend  ---->  PostgreSQL (users, products, listings, subscriptions)
        |
        +----> Redis (Celery broker/backend -- no tasks registered yet)
        |
        +----> Stripe (checkout sessions + webhooks)

scraper/ (separate package, not yet invoked by any backend code path)
```

See `docs/ARCHITECTURE.md` for more detail.

## 3. Tech stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, python-jose (JWT), passlib+bcrypt, Stripe SDK
- **Frontend:** React, TypeScript, Vite, Tailwind, recharts, lucide-react
- **Scraper:** httpx, BeautifulSoup
- **Infra:** Docker, Docker Compose, GitHub Actions

## 4. Main features (implemented)

- Register / log in (JWT-based)
- Create and list tracked products with marketplace listings
- Per-user data isolation (verified by test: a second user cannot see or
  fetch another user's products)
- Real Stripe Checkout for Professional/Enterprise plans, with webhook
  handling that updates subscription status
- Liveness (`/health/live`) and readiness (`/health/ready`, checks
  Postgres + Redis) endpoints
- One working scraper adapter (`books.toscrape.com`) with price/
  availability normalization handling US, EU, and Indian price formats

## 5. Repository structure

```
priceloop/
├── backend/
│   ├── app/            # FastAPI app: api/, models/, schemas/, services/, core/
│   ├── alembic/         # migrations
│   └── tests/           # pytest suite (auth, products, billing, health)
├── frontend/            # Vite + React dashboard
├── scraper/              # adapters, normalization, fixture-based tests
├── docker-compose.yml           # local dev (hot-reload, bind mounts)
├── docker-compose.prod.yml      # production (no bind mounts, one-shot migrate step)
├── .github/workflows/ci.yml
└── docs/
    ├── ROADMAP.md
    ├── SRS.md
    ├── ARCHITECTURE.md
    └── PROJECT_STATUS.md         # <- read this for an honest implemented/planned split
```

## 6. Local development setup

```bash
git clone <your fork>
cd priceloop
cp .env.example .env
# generate a real secret instead of the placeholder:
sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/" .env && rm .env.bak

docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: run separately for now (see section 11) -- it isn't in
  `docker-compose.yml` since Vite's dev server is normally run directly

## 7. Environment variables

See `.env.example` (root, for the backend) and `frontend/.env.example`
(for the frontend). Every variable is commented with what it does and
whether it's actually read by any code yet or reserved for a future
phase. Never commit a real `.env` -- it's gitignored everywhere in this
repo on purpose.

## 8. Database migrations

Schema is managed by Alembic (`backend/alembic/`), not by wildly running
`create_all()` against a production database.

```bash
cd backend
alembic upgrade head      # apply pending migrations
alembic downgrade -1      # roll back one migration
alembic revision --autogenerate -m "description"   # create a new migration after changing models
```

In `docker-compose.prod.yml`, a dedicated `migrate` service runs
`alembic upgrade head` once and exits; `backend` and `worker` wait for it
to complete successfully before starting, so migrations never race
against app startup or run redundantly per worker.

Local dev (`docker-compose.yml`) skips this ceremony and just calls
`create_all()` on startup for faster iteration -- fine for a dev database
you don't mind recreating, not how production works.

## 9. Running the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 10. Running Celery

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

Note: the Celery app is real and starts cleanly, but no tasks are
registered yet -- there's nothing for it to actually do until scraping
scheduling (a planned phase) is built.

## 11. Running the frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if the backend isn't on localhost:8000
npm run dev
```

## 12. Running tests

```bash
# Backend (30 tests: auth, products, billing, health)
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v

# Scraper (11 tests: adapter parsing, price/availability normalization)
cd ..
PYTHONPATH=. python -m pytest scraper/tests/ -v

# Frontend
cd frontend
npx tsc --noEmit
npm run build
```

## 13. Production Docker deployment

```bash
cp .env.example .env   # fill in real SECRET_KEY, STRIPE_*, POSTGRES_* values
docker compose -f docker-compose.prod.yml up --build
```

This uses a repo-root build context (see `backend/Dockerfile`'s top
comment for why -- the previous `context: ./backend` silently excluded
the `scraper/` package from the image), runs as a non-root user, has no
`--reload`, and does not publish Postgres/Redis ports to the host.

**Not verified in this repository's dev environment:** an actual
`docker build`/`docker compose up` run against these files -- Docker
itself wasn't available in the sandbox this was built in. The Dockerfile
was validated by simulating its exact file layout and confirming both
`app.*` and `scraper.*` imports resolve correctly from it; the compose
files were validated for YAML correctness. Please run a real build before
trusting this in production.

## 14. CI/CD

`.github/workflows/ci.yml` runs on every push/PR: backend tests against
real Postgres/Redis service containers (including an Alembic
upgrade+downgrade check against real Postgres), and a frontend
type-check + build. **Not verified:** an actual run on GitHub's runners
-- the YAML is syntactically valid and the same commands pass locally,
but it hasn't executed on GitHub Actions itself yet (that only happens
once this is pushed).

## 15. API documentation

Auto-generated by FastAPI at `/docs` (Swagger UI) and `/redoc` once the
backend is running.

## 16. Security notes

- `SECRET_KEY` defaults to a placeholder that **refuses to let the app
  boot** if `ENVIRONMENT=production` and it hasn't been changed
- Passwords are hashed with bcrypt via passlib (pinned versions --
  `bcrypt>=5` breaks passlib 1.7.4, see git history)
- CORS origins are configurable (`CORS_ORIGINS`), default `*` for local
  dev only
- Stripe webhook signatures are verified before any subscription state
  changes
- **Not yet implemented:** rate limiting on login/register (real risk at
  any real scale), refresh tokens, RBAC enforcement beyond a stored role
  field

## 17. Known limitations

See `docs/PROJECT_STATUS.md` for the full, explicit list. Short version:
no analytics, product matching, anomaly detection, forecasting, or
alerts exist yet; only one scraper adapter exists (a scraping-practice
site, not a real marketplace); the Alembic migration and Docker build
have not been tested against real Postgres/Docker in this environment
(only simulated/SQLite-verified).

## 18. Future improvements

Tracked in `docs/ROADMAP.md`, phase by phase. Near-term priorities per
`docs/PROJECT_STATUS.md`: rate limiting on auth endpoints, running the
Alembic migration and Docker build against real infrastructure at least
once, then cross-marketplace product matching and scheduling (Celery
tasks that actually invoke the scraper).
