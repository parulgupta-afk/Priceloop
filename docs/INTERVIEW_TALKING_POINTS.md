# Interview talking points

## Architecture
- Sync SQLAlchemy Session on HTTP handlers for consistency; Celery tasks open their own sessions.
- Redis: rate limits + short cache + broker — Postgres remains source of truth.
- Observations are append-only; listings hold latest snapshot only.

## Hardest bugs / trade-offs
- Dual async/sync API modules: resolved by deprecating unmounted async routers and keeping one mounted surface.
- Fail-open rate limits if Redis is down (availability vs strict limiting).
- Matching must penalize storage/color variants to avoid false merges.

## AI design
- Planner selects tools from the user query; tools re-check `user_id`.
- Response includes tool_trace and limitations for auditability.
- LLM keys optional — deterministic path works offline.

## Security
- Production refuses weak SECRET_KEY, SQLite, wildcard CORS.
- Object-level checks on product and alert routes.
- Stripe webhooks verified when configured.

## What you’d do next
- Official retailer APIs, email delivery, pgvector only after fuzzy baseline metrics, public staging URL.
