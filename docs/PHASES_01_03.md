# Phases 0 – 3 Summary (Current Batch)

## Phase 0 — Project Foundation (Completed)

- Professional monorepo layout
- Docker Compose with PostgreSQL 16 (pgvector) + Redis
- `.env.example`, `.gitignore`, MIT License, README
- Core documentation (Roadmap, Architecture, Database ER)
- Alembic configuration (env.py + script template) ready for first migration

## Phase 1 — User Authentication (Completed)

- JWT access + refresh tokens
- Argon2 password hashing
- Roles: USER / ANALYST / ADMIN
- Endpoints:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `GET  /api/v1/auth/me`
- FastAPI dependency injection for current user + role checks

## Phase 2 — Product Management (Completed)

- Models: `Product`, `Source`, `ProductListing`, `PriceObservation`
- Full CRUD for products
- Attach listings to a product (auto-creates Source if needed)
- Ownership checks on every operation
- Pydantic schemas for request/response validation

## Phase 3 — First Scraper + Normalization + Price Pipeline (Started & Working)

- `BaseScraper` abstract interface
- Working `DemoScraper` (fixture HTML – perfect for demos)
- Normalization helpers (price, currency, availability, title)
- `scrape_service` that:
  1. Loads listing + source
  2. Runs the correct adapter
  3. Normalizes data
  4. Updates listing snapshot
  5. Creates a `PriceObservation`
- Manual trigger endpoint: `POST /api/v1/listings/{id}/scrape`
- Price history endpoint: `GET /api/v1/products/{id}/prices`
- Celery skeleton + `scrape.listing` background task

---

## Vertical Slice You Can Run Right Now

1. Register → Login → Create Product
2. Attach a listing with `source_name = "demo"`
3. Call the scrape endpoint
4. Fetch price history

This proves the complete path from user action → scraper → normalized data → database → API.
