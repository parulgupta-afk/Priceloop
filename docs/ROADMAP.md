# Priceloop — Roadmap

Build vertically. Do not attempt scraping + Redis/Celery + LLM + forecasting +
self-healing all in week one -- each phase should produce something runnable.

- [x] Phase 0 — Project foundation (repo, docs, stack decisions)
- [x] Phase 1 — Repository + architecture skeleton
- [x] Phase 2 — Authentication (register, login, JWT, roles)
- [x] Phase 3 — Product management (create/track products + listings) <- current
- [ ] Phase 4 — First scraper (single source, base adapter interface)
- [ ] Phase 5 — Normalization (price/currency/availability into canonical schema)
- [ ] Phase 6 — Core database schema
- [ ] Phase 7 — Price history + derived metrics
- [ ] Phase 8 — Scheduling
- [ ] Phase 9 — Redis + Celery workers
- [ ] Phase 10 — Product matching across sources (confidence-scored)
- [ ] Phase 11 — Competitive analytics (positioning, market average/median)
- [ ] Phase 12 — Dashboard v1
- [ ] Phase 13 — Anomaly detection (statistical first)
- [ ] Phase 14 — Price forecasting (moving average -> regression -> later ML)
- [ ] Phase 15 — AI insight engine (LLM over structured analytics context)
- [ ] Phase 16 — Natural language query
- [ ] Phase 17 — Smart alerts (rule engine + severity)
- [ ] Phase 18 — Notifications (email, Slack, webhook)
- [ ] Phase 19 — Scraper observability
- [ ] Phase 20 — Self-healing scraper (AI suggests selector fix, human approves)
- [ ] Phase 21 — Screenshot verification
- [ ] Phase 22 — Cost intelligence
- [ ] Phase 23 — Security hardening
- [ ] Phase 24 — Testing (unit, integration, e2e)
- [ ] Phase 25 — Dockerization
- [ ] Phase 26 — CI/CD
- [ ] Phase 27 — Production deployment
- [ ] Phase 28 — Final polish
- [ ] Phase 29 — Demo mode (seeded dataset for reliable presentations)

## Sprint grouping (suggested)

1. Auth, products, database, basic UI
2. Scraper, listings, price observations
3. Scheduler, Redis, Celery
4. Analytics, charts, competitor comparison
5. Product matching
6. Alerts
7. Anomaly detection
8. Forecasting
9. LLM insights
10. Natural-language queries
11. Scraper health
12. Self-healing scraper
13. Cost dashboard, observability
14. Testing, security, Docker, CI/CD
15. Production deployment, documentation, demo
