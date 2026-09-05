# PriceLoop — Project Status

Honest status for portfolio / interviews. Prefer this over outdated marketing claims.

## Implemented (working foundation)

| Area | Status | Notes |
|------|--------|-------|
| Auth (JWT + Argon2 + RBAC) | Done | USER / ANALYST / ADMIN |
| Products & Listings | Done | CRUD + ownership |
| Scraping (adapter pattern) | Done | Demo adapter + BaseScraper |
| Normalization | Done | Price, currency, availability, title |
| Price history | Done | PriceObservation time-series |
| Analytics | Done | min/max/avg/median/volatility/position |
| Product matching | Done | Fuzzy + confidence levels |
| Anomaly detection | Done | Z-score, IQR, % deviation (statistical, not deep learning) |
| Forecasting | Done | Moving average + exponential smoothing + trend + confidence band |
| AI Insights | Done | Structured analytics context → template / LLM-ready (Gemini/OpenAI via config) |
| Natural language query | Done | Intent → deterministic services |
| Smart alerts | Done | Rules + evaluate endpoint |
| Celery jobs + beat | Done | scrape.listing + scrape.all_active |
| Scraper health | Done | Success rate, per-source, duration |
| Self-healing selectors | Done | Human-approval gate |
| Cost intelligence | Done | Category totals |
| Security headers | Done | Basic hardening middleware |
| Unit tests | Partial | Normalization + matching (expand coverage) |
| Frontend | Done | **React 19 + Vite 6 + TypeScript + Tailwind** (not Next.js) |
| Frontend ↔ API | Done | JWT client, products/prices/analytics mapping, live/offline banner |
| Product images | Done | ProductThumb + seed image URLs |
| Docker (dev) | Done | Postgres + Redis via compose; API run locally with uvicorn |
| Docker (prod compose) | Present | backend + worker services defined |
| Demo seed script | Done | Multi-product catalog + listings + price history |

## Planned / not fully verified in CI

| Item | Notes |
|------|--------|
| Integration tests (TestClient) | Recommended next |
| GitHub Actions CI | Config may be partial — treat as planned until green pipelines exist |
| Prometheus + Grafana export | Observability target; structured logging exists |
| Real marketplace adapters | Prefer official APIs / respect ToS |
| sentence-transformers + pgvector matching | Schema ready; full embedding pipeline can be deepened |
| Screenshot storage (S3) | Optional env vars; not required for core path |

## How to run (dev)

```bash
docker compose up -d postgres redis

cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Seed
python -m scripts.seed_demo

# Frontend
cd ../frontend
npm install
npm run dev
```

- App: http://localhost:3000  
- API: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

Demo login after seed: `demo@priceloop.local` / `demo12345`

## Interview talking points (accurate)

- Async pipeline: FastAPI → Redis/Celery → scrape/analytics → PostgreSQL  
- Statistical anomaly/forecasting, not “deep learning black box”  
- LLM only on **structured context**, not raw hallucination  
- Adapter-based scraping with rate limits and human-gated selector changes  
- JWT + RBAC, ownership checks on product routes  

## Portfolio one-liner

> Distributed price-intelligence platform with automated data collection, product entity resolution, time-series analytics, statistical anomaly detection and forecasting, LLM-ready market insights, async job processing, alerting, and human-gated scraper maintenance.
