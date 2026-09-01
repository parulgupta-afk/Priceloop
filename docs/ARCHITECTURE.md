# Architecture

\`\`\`
E-commerce sites
      |
      v
Scraping engine (adapters, rate limiter, retry manager)
      |
      v
Data pipeline (validate, normalize, dedupe, product matching)
      |
      v
PostgreSQL + Redis (time-series price data, job queues, cache)
      |
      +---------------+----------------+
      v               v                v
Analytics engine   ML/forecasting   Alert engine
      |               |                |
      +---------------+----------------+
                      |
                      v
                 FastAPI backend
                      |
                      v
              React/Next.js dashboard
\`\`\`

## Layering rule

Each layer only talks to the layer directly above/below it. The scraper
never touches the LLM; the dashboard never touches raw HTML. Everything
downstream of the data pipeline works off the same canonical ProductData
schema (see scraper/core/base_scraper.py). This is what makes it possible
to swap a proxy provider, database, or LLM without a rewrite.
