# Software Requirements Specification (condensed)

## Scope
User management, multi-source price collection, normalization, product
matching, historical analytics, competitive analysis, anomaly detection,
forecasting, AI-generated insights, natural-language queries, alerting,
scraper monitoring, admin controls.

## Key functional requirements
- FR-06 Automated, scheduled scraping per source
- FR-09/10 Product matching across sources with a confidence score
- FR-13 Anomaly detection on price movements
- FR-14 Short-term price forecasting with a confidence interval
- FR-15 AI-generated natural-language explanations, grounded in structured
  analytics context (not free-form generation) to reduce hallucination
- FR-20/21 Self-healing scraper suggestions, gated behind human approval

## Non-functional requirements
- Scale to 10,000+ SKUs across 5+ sources without redesign
- Adding a new source requires a new adapter + fixtures only
- Every AI output (match, anomaly, forecast) carries a confidence score
- Scrape failures must be visible within one scrape cycle, not silent
