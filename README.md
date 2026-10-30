# PriceLoop

**Autonomous, Production-Grade E-Commerce Price Intelligence & Competitor Tracking Platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI: 0.115+](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Docker: Ready](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

---

## Table of Contents

- [Overview & Key Capabilities](#overview--key-capabilities)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
  - [Option B: Local Manual Setup](#option-b-local-manual-setup)
- [Seeding Demo Data](#seeding-demo-data)
- [API Reference](#api-reference)
- [Analytics & Intelligence Engines](#analytics--intelligence-engines)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Security Hardening & Production Validation](#security-hardening--production-validation)
- [License](#license)

---

## Overview & Key Capabilities

PriceLoop is an end-to-end pricing intelligence engine designed for modern e-commerce brands and multi-channel retailers. It tracks competitor listings, captures time-series price snapshots, applies deterministic and statistical anomaly detection, calculates match confidences across product catalogs, and delivers actionable, evidence-grounded pricing recommendations.

### Highlights

- **Multi-Tenant Data Isolation:** Strict user boundaries across products, listings, alerts, and subscription tiers.
- **Resilient Web Scraping Engine:** Modular adapter architecture with exponential backoff, user-agent rotation, per-domain rate limiting, and currency normalization (handling USD, EUR, and INR formats).
- **Time-Series Price Analytics:** Deterministic rolling statistics (min, max, mean, standard deviation, spread) with Redis cache-aside caching.
- **Statistical Anomaly Detection:** Real-time flagging of price spikes, flash drops, and currency errors using Z-score, Interquartile Range (IQR), Median Absolute Deviation (MAD), and percentage delta models.
- **Catalog Matching Engine:** Multi-attribute fuzzy scoring (title token matching, brand resolution, model verification) with machine-readable explainability logs.
- **Enterprise Stripe Billing:** Full checkout session lifecycles, webhook event verification, and automatic subscription state transitions (Free, Professional, Enterprise).
- **Production Observability:** Dual-stage health checks (`/health/live`, `/health/ready`), Prometheus-ready `/metrics` counters, and distributed Request-ID middleware.

---

## System Architecture

```text
+-----------------------------------------------------------------------------------+
|                                Client Layer                                       |
|                  React 19 Dashboard (Vite, TypeScript, Tailwind)                  |
+-----------------------------------------------------------------------------------+
                                          |
                                          | REST API / JWT Bearer
                                          v
+-----------------------------------------------------------------------------------+
|                             FastAPI Gateway Layer                                 |
|  - Request-ID Middleware         - Redis Token Bucket Rate Limiting               |
|  - CORS Security Policy          - Fail-Fast Config Validation                    |
+-----------------------------------------------------------------------------------+
       |                    |                       |                    |
       v                    v                       v                    v
+--------------+   +-------------------+   +------------------+   +-----------------+
| Auth & Users |   | Product Catalog   |   | Pricing Engine   |   | Stripe Billing  |
| (JWT/bcrypt) |   | (CRUD & Search)   |   | (Analytics/MAD)  |   | (Webhooks)      |
+--------------+   +-------------------+   +------------------+   +-----------------+
       |                    |                       |                    |
       +--------------------+-----------+-----------+--------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                             Storage & Cache Layer                                 |
|  - PostgreSQL 16 (Relational Schema & Time-Series Price Observations)             |
|  - Redis 7 (Cache-Aside Engine, Celery Message Broker, Distributed Locks)         |
+-----------------------------------------------------------------------------------+
                                        ^
                                        | Asynchronous Task Execution
                                        v
+-----------------------------------------------------------------------------------+
|                            Asynchronous Worker Layer                              |
|  - Celery Worker: Dynamic Scraping Jobs, Cooldowns, Batch Normalization           |
|  - Celery Beat: Scheduled Periodic Monitoring & Rule Evaluation                   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                            External Ingestion Adapters                            |
|  - E-Commerce Targets (books.toscrape.com, demo marketplaces)                     |
+-----------------------------------------------------------------------------------+
```

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.12+), Pydantic v2, Pydantic-Settings |
| **ORM & Database** | SQLAlchemy 2.0, Alembic (Migrations), PostgreSQL 16, SQLite (local fallback) |
| **Cache & Task Queue** | Redis 7, Celery, Celery Beat |
| **Authentication & Security** | JWT (python-jose), Passlib (Bcrypt), OAuth2 Password Bearer |
| **Payments** | Stripe SDK (Hosted Checkout & Webhooks) |
| **Scraper & Extraction** | HTTPX, BeautifulSoup4, Custom Normalization Pipeline |
| **Frontend UI** | React 19, TypeScript, Vite 6, Tailwind CSS v4, Lucide Icons, Recharts |
| **DevOps & Testing** | Docker, Docker Compose, Pytest, GitHub Actions CI |

---

## Repository Structure

```text
priceloop/
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated CI test pipeline
├── backend/
│   ├── alembic/                 # Database migration scripts
│   ├── app/
│   │   ├── api/                 # Endpoint routers (auth, products, prices, billing, intel)
│   │   ├── core/                # Config, database engine, security, metrics, middleware
│   │   ├── models/              # SQLAlchemy relational models (User, Product, Listing, Alert)
│   │   ├── schemas/             # Pydantic request/response validation schemas
│   │   ├── services/            # Business logic (analytics, anomalies, matching, billing)
│   │   └── workers/             # Celery worker application & task declarations
│   ├── scripts/                 # Demo seeding, benchmarks, and load testing scripts
│   ├── tests/                   # Comprehensive backend test suite (Pytest)
│   ├── Dockerfile               # Production container image definition
│   └── requirements.txt         # Pinned Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client utilities and mappings
│   │   ├── components/          # Reusable UI views, modals, and charts
│   │   ├── context/             # Authentication and global state providers
│   │   └── lib/                 # Core HTTP request client
│   ├── package.json             # Frontend package manifest
│   └── vite.config.ts           # Vite build and dev server configuration
├── scraper/
│   ├── adapters/                # Modular marketplace scraper adapters
│   ├── core/                    # Base scraper definitions and interfaces
│   └── tests/                   # Scraper unit tests and fixture parsers
├── docs/                        # Architecture decision records, specifications, and audit logs
├── docker-compose.yml           # Local development composition (hot reloading)
├── docker-compose.prod.yml      # Production composition (one-shot migration runner)
└── README.md                    # Project documentation
```

---

## Getting Started

### Prerequisites

- **Python:** 3.12 or newer
- **Node.js:** 20.x or newer (npm included)
- **Docker & Docker Compose:** Optional for local dev, required for containerized deployment

### Environment Configuration

1. Copy the root environment template:

   ```bash
   cp .env.example .env
   ```

2. Copy the frontend environment template:

   ```bash
   cp frontend/.env.example frontend/.env
   ```

3. Configure your required keys in `.env`:
   - `ENVIRONMENT`: Set to `development` for local machines, or `production` for strict fail-fast validation.
   - `SECRET_KEY`: Minimum 32-character random string.
   - `DATABASE_URL`: Connection string to PostgreSQL (`postgresql://priceloop:priceloop@localhost:5432/priceloop`).
   - `REDIS_URL`: Connection string to Redis (`redis://localhost:6379/0`).
   - `CORS_ORIGINS`: Comma-separated list of allowed origins (e.g., `http://localhost:3000`, `http://localhost:5173`).

---

### Option A: Docker Compose (Recommended)

Run the entire full-stack application (PostgreSQL, Redis, FastAPI Backend, Celery Worker) with one command:

```bash
docker compose up --build
```

- **Backend API:** [`http://localhost:8000`](http://localhost:8000)
- **API Documentation (Swagger UI):** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Frontend Dev Server:** Launch separately in the `frontend/` directory (see below).

---

### Option B: Local Manual Setup

#### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations (if PostgreSQL is running)
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*(Note: In `ENVIRONMENT=development`, if PostgreSQL is not reachable, the backend automatically and safely falls back to local SQLite at `backend/test.db` for instant offline development).*

#### 2. Celery Worker (Optional for Background Scraping)

In a separate terminal:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

#### 3. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend dashboard will be available at [`http://localhost:3000`](http://localhost:3000).

---

## Seeding Demo Data

To populate your database with realistic products, marketplace listings, and 30-day historical price observation series:

```bash
cd backend
python -m scripts.seed_demo_sync
```

Default credentials created for local exploration:

- **Email:** `demo@priceloop.ai`
- **Password:** `Demo123!`

You can also click the **"Fill Demo Credentials"** button on the frontend login screen to authenticate instantly.

---

## API Reference

Interactive API documentation and schema explorers are hosted automatically:

- **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

### Key Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health/live` | Process liveness check |
| **Health** | `GET` | `/health/ready` | Dependency readiness (verifies Postgres & Redis) |
| **Metrics** | `GET` | `/metrics` | Process performance & request counters |
| **Auth** | `POST` | `/api/auth/register` | Register new user account |
| **Auth** | `POST` | `/api/auth/login` | Authenticate & receive JWT bearer token |
| **Auth** | `GET` | `/api/auth/me` | Fetch authenticated user profile |
| **Catalog** | `GET` | `/api/products` | List tracked products (supports `?skip=` and `?limit=`) |
| **Catalog** | `POST` | `/api/products` | Create tracked product with marketplace listings |
| **Catalog** | `GET` | `/api/products/{id}` | Retrieve product details by UUID |
| **Prices** | `GET` | `/api/products/{id}/prices` | Fetch time-series price observation history |
| **Prices** | `GET` | `/api/products/{id}/analytics` | Compute rolling statistical summary & margin metrics |
| **Prices** | `POST` | `/api/listings/{id}/scrape` | Trigger on-demand listing scrape |
| **Intelligence** | `POST` | `/api/intelligence/anomalies` | Execute multi-model statistical anomaly detection |
| **Intelligence** | `POST` | `/api/intelligence/matching` | Compute catalog match confidence with explanation |
| **Alerts** | `GET` | `/api/alerts` | List configured user price alerts |
| **Alerts** | `POST` | `/api/alerts` | Create automated threshold or percentage alert |
| **Billing** | `GET` | `/api/billing/subscription` | Fetch active user subscription status |
| **Billing** | `POST` | `/api/billing/create-checkout-session` | Initialize Stripe Checkout session |
| **Billing** | `POST` | `/api/billing/webhook` | Process signed Stripe webhook notifications |

---

## Analytics & Intelligence Engines

### 1. Statistical Anomaly Detection

Located in [`backend/app/services/anomaly_service.py`](backend/app/services/anomaly_service.py), PriceLoop evaluates price movements across multiple concurrent algorithms:

- **Z-Score:** Flags standard deviation outliers ($\vert z \vert > 2.5$).
- **Interquartile Range (IQR):** Identifies observations beyond $1.5 \times \text{IQR}$ fences, resilient against extreme historical skew.
- **Median Absolute Deviation (MAD):** Non-parametric outlier assessment suited for volatile retail catalogs.
- **Percentage Threshold:** Immediate alerts for single-interval price changes exceeding configured bounds (e.g., $\ge 30\%$).

### 2. Product Matching & Explainability

Located in [`backend/app/services/matching_service.py`](backend/app/services/matching_service.py), PriceLoop reconciles identical products across disparate retailers:

- **Token Overlap:** Normalized Jaccard similarity across brand-stripped product titles.
- **Brand & Model Disambiguation:** Exact and phonetic brand checks coupled with model number extraction.
- **Score Breakdown:** Outputs both aggregate match confidence ($[0.0, 1.0]$) and human-readable reasoning strings.

---

## Testing & Quality Assurance

PriceLoop maintains high test coverage across unit, integration, and parser boundaries.

```bash
# Run backend test suite (56 test cases)
cd backend
python -m pytest tests/ -v

# Run scraper adapter & normalization tests (11 test cases)
cd ..
PYTHONPATH=".;scraper;backend" python -m pytest scraper/tests/ -v

# Run frontend TypeScript type checking
cd frontend
npm run lint

# Run frontend production build
npm run build
```

---

## Security Hardening & Production Validation

When running with `ENVIRONMENT=production`, the application performs strict fail-fast validation on startup:

- **Secret Key:** Must be at least 32 characters and cannot use default/insecure placeholders.
- **Database Connection:** Must be a valid PostgreSQL connection (`postgresql://` or `postgresql+asyncpg://`). SQLite is strictly prohibited in production.
- **Redis Connection:** Must be a valid Redis connection string (`redis://` or `rediss://`).
- **CORS Protection:** Must declare explicit, comma-separated allowed origins. Wildcards (`*`) are disallowed.
- **Storage Credentials:** Default MinIO credentials (`minioadmin`) are prohibited.
- **Rate Limiting:** Protects `/api/auth/login` (5/min) and `/api/auth/register` (3/min) against brute-force attacks via Redis token buckets.

---

## License

This project is licensed under the [MIT License](LICENSE).
