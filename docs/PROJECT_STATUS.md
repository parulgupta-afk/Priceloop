# PriceLoop — Project Status (v0.6)

## Implemented
- Auth (JWT, bcrypt, rate limits)
- Products + search + ownership isolation
- Price observations + history API + analytics
- Scraper adapters (demo, books.toscrape) + Celery cooldown/beat
- Redis rate limiting + cache-aside
- Anomaly detection (z/IQR/%/MAD)
- Product matching scores
- Grounded insights
- Alerts CRUD + evaluate
- Stripe billing hooks
- Health live/ready, metrics, request IDs
- Docker Compose, Alembic, CI, load_test script, demo seed

## Future / optional
- Live Amazon/etc. adapters (terms-compliant)
- Full LLM provider wiring for insights
- Prometheus/Grafana exporters
- Kubernetes, multi-region
