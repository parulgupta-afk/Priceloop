# PriceLoop 2.0 architecture (as implemented)

```
React (Vite) + JWT
        |
        v
FastAPI  (v1.0.0)  -- Request ID middleware, rate limits
   |-- /api/auth
   |-- /api/products
   |-- /api/billing (Stripe)
   |-- /api prices / intelligence / ai/query / forecast / scrape-jobs
   |
   +--> PostgreSQL (users, products, listings, observations, alerts, scrape_jobs, subscriptions)
   +--> Redis (limits, cache, Celery)
   +--> Celery worker + beat (scrape.listing, scrape.all_active)
   +--> scraper adapters (demo, books_toscrape)
```

**AI path:** `POST /api/ai/query` → deterministic planner → tools (analytics, anomalies, matches, alerts) → grounded answer.

**Not in tree as production defaults:** unrestricted marketplace HTML scrapers, pgvector, hosted LLM-only answers without tools.
