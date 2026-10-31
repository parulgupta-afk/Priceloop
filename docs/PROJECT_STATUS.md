# PriceLoop — Project Status (2.0 track, API v1.0.0)

## Implemented
- Auth (JWT, bcrypt, rate limits), multi-tenant products
- Price observations + history, analytics, summary endpoint
- Scraper adapters (demo, books.toscrape), Celery cooldown/beat, scrape_jobs audit
- Redis rate limiting + cache-aside
- Anomaly detection (z/IQR/%/MAD)
- Hybrid matching with variant penalties
- Alerts + evaluate-deduped notifications
- Grounded AI analyst (`POST /api/ai/query` tool calling)
- Experimental forecast with baselines + disclaimer
- Stripe billing hooks
- Health live/ready, metrics, request IDs
- Docker Compose, Alembic, CI, load_test, seed_demo_sync (books.toscrape)
- Frontend: API client base fixed, empty mocks, load catalog on login
- Portfolio docs: DEMO_SCRIPT, PORTFOLIO, INTERVIEW_TALKING_POINTS, SECURITY_CONTROLS

## Explicitly not claimed
- Live scraping of ToS-restricted major retailers without official APIs
- High-confidence production price prediction
- Multi-region Kubernetes by default
