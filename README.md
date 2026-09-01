# Priceloop

An AI-powered competitive pricing intelligence platform that collects public e-commerce pricing data, matches products across marketplaces, analyzes historical trends, detects anomalies, forecasts price movements, and generates actionable pricing recommendations and alerts.

## Quick start

\`\`\`bash
cp .env.example .env
docker compose up --build
\`\`\`

Backend API: http://localhost:8000/health
API docs: http://localhost:8000/docs

## Project structure

- \`backend/\` — FastAPI application (auth, products, analytics, alerts, insights)
- \`scraper/\` — site adapters, request/retry/rate-limit management
- \`ml/\` — product matching, anomaly detection, forecasting
- \`frontend/\` — React/Next.js dashboard
- \`docs/\` — ROADMAP, SRS, DRD, ARCHITECTURE

## Development phases

See \`docs/ROADMAP.md\` for the full phased build plan. Current phase: **Phase 0 — Project Foundation**.

## Note on scraping scope

This project scrapes only publicly accessible product pages, respects per-site rate limits, and is built for research/portfolio purposes. It does not target authenticated or access-restricted content.
