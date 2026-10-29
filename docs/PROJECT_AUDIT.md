# PriceLoop — Project Audit (updated after Phases 0–7)

| Component | Status | Notes |
|-----------|--------|-------|
| Auth | Done + rate limited | login 5/min, register 3/min |
| Products | Done + search | q, skip, limit |
| Price history | Done | observations + GET prices + cache |
| Analytics | Done | deterministic stats endpoint |
| Ingestion | Done | demo + books_toscrape, Celery cooldown |
| Rate limiting | Done | Redis fixed-window, fail-open |
| Caching | Done | prices + analytics TTLs |
| Stripe | Done | prior commits |
| Alerts / AI / matching | Scaffold only | next phases |
