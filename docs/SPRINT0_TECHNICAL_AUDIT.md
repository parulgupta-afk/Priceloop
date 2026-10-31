# PriceLoop 2.0 — Sprint 0 Technical Audit

**Audit date:** 2026-10-31  
**Baseline:** GitHub `main` @ `db42d48` (2026-10-30) and nearby commits  
**Scope:** Backend, frontend, scraper, infra, security, gap vs PriceLoop 2.0 roadmap  

---

## 1. Executive summary

| Area | Verdict |
|------|---------|
| Auth + multi-tenant products | **Working** (JWT, ownership tests) |
| Price observations + history | **Working** (models + sync API via `prices` / `intelligence`) |
| Scraper (books.toscrape + demo) | **Working path**; only permitted/demo sources |
| Rate limit + Redis cache + Celery | **Present** |
| Anomaly / matching / alerts / grounded insights | **Present** on mounted `intelligence` router |
| Parallel `api/analytics.py`, `api/ai.py`, `api/admin.py` | **Not mounted** — dead / async drift |
| Frontend | **UI scaffold strong**; still mixes **mockData** with API |
| Alembic vs models | **Drift risk** (create_all in dev; migration lag) |
| Live retailer scrapers / LLM tool-calling / pgvector / ML forecast | **Not production-ready** |
| Deployed public URL | **Not verified in this audit** |

**Bottom line:** Foundation is stronger than a typical student CRUD app. PriceLoop 2.0 should **not** rewrite from zero. Priority is (1) kill dual async/sync stacks, (2) mount or delete orphan routers, (3) wire frontend to real APIs only, (4) then AI analyst with **tool calling + user isolation**.

---

## 2. Latest commits (remote)

| SHA | Message | Date |
|-----|---------|------|
| db42d48 | chore: update local demo database with seeded real-world products | 2026-10-30 |
| 46a05ce | feat: add end-to-end smoke test script for backend APIs | 2026-10-30 |
| cdd2c12 | feat: add SettingsView component | 2026-10-30 |
| 32f8aff | feat: implement database models… | 2026-10-30 |
| df96cab | test(intelligence): matching edge cases and alert evaluation | 2026-10-30 |
| a0852b4 | refactor: FastAPI lifespan context manager | 2026-10-30 |
| f839d6e | refactor: Pydantic V2 ConfigDict | 2026-10-30 |
| 920202e | docs: demo credentials and test suite count | 2026-10-30 |
| db7324f | feat: scrape service and demo seed | 2026-10-29 |
| a6953f6 | feat: frontend core structure | 2026-10-29 |

App version in code: **0.6.0**.

---

## 3. Architecture (as implemented)

```
React (Vite) ──JWT──> FastAPI (sync SessionLocal primarily)
                         │
                         ├── PostgreSQL (users, products, listings, observations, alerts, subscriptions)
                         ├── Redis (Celery broker, rate limits, short cache)
                         ├── Celery worker + beat (scrape.listing, scrape.all_active)
                         └── Stripe (checkout + webhook)
scraper/ ── adapters (demo, books_toscrape) ── scrape_service
```

**Mounted routers only:**
- `/api/auth/*`
- `/api/products/*`
- `/api/billing/*`
- `/api/*` from `prices.py` (history, analytics, scrape trigger)
- `/api/*` from `intelligence.py` (anomalies, matches, insights, alerts)
- `/health`, `/health/live`, `/health/ready`, `/metrics`

**NOT mounted (code exists, unreachable via main):**
- `api/analytics.py` (async + AsyncSession)
- `api/ai.py` (async insights/alerts duplicate)
- `api/admin.py` (scraper health, selector proposals, costs)

---

## 4. Feature verification matrix

| Feature | Code | Mounted | Tested | Notes |
|---------|------|---------|--------|-------|
| Register / login / me | Yes | Yes | Yes | Rate limited |
| Product CRUD + ownership | Yes | Yes | Yes | Isolation tests |
| Product search `?q=` | Yes | Yes | Partial | |
| Price history | Yes | Yes | Partial | Cache optional |
| Manual scrape | Yes | Yes | Smoke | books_toscrape / demo |
| Celery scrape + cooldown | Yes | Worker | Limited | Beat schedule present |
| Analytics (min/max/avg/%) | Yes | Via prices/intelligence | Partial | |
| Anomaly z/IQR/%/MAD | Yes | intelligence | Unit | |
| Product matching fuzzy | Yes | intelligence | Unit | No embeddings yet |
| Alerts CRUD + evaluate | Yes | intelligence | Yes | |
| Grounded insights | Yes | intelligence | Shape test | Rule-based; LLM optional |
| Stripe checkout/webhook | Yes | Yes | Yes | Needs real keys |
| Admin / self-healing | Scaffold | **No** | No | |
| Forecast API | In analytics.py | **No** | No | Experimental only if mounted |
| NL AI query / tool calling | ai.py partial | **No** | No | 2.0 flagship gap |
| pgvector RAG | No | — | — | |
| Frontend live data only | Partial | — | — | **mockData.ts** still used |

---

## 5. Database audit

**Models present:** User, Source, Product, ProductListing, PriceObservation, Alert (+ enums), Subscription, matching-related models (file present).

**Strengths**
- Observations as append-only history (correct design).
- User FK on products; ownership checks in services/APIs.
- Numeric prices (not float-only chaos).
- Portable JSON for SQLite tests vs Postgres.

**Risks / debt**
1. **Alembic lag:** Initial migration is thin; second migration adds observations/sources; runtime often relies on `create_all` in non-production lifespan.
2. **Duplicate conceptual models:** Roadmap wants Competitor, ScrapingJob, AIInsight, Forecast — some overlap with existing Alert/Source/observations; avoid parallel tables without migration plan.
3. **Indexes:** History index migration exists; verify applied on real Postgres.
4. **Sync vs async:** `get_db` is sync Session; orphan routers expect AsyncSession → would crash if mounted as-is.

---

## 6. Scraper & data pipeline audit

| Item | Status |
|------|--------|
| Adapter interface | Present (`BaseScraper` / books adapter fetch+parse) |
| Registry | demo + books_toscrape |
| Normalization | Currency/availability helpers + tests |
| Retries / backoff | resilience helper + Celery retries |
| Rate limit outbound | Partial (source field + scraper rate_limiter module) |
| Idempotency | Cooldown on listing; not full unique observation key |
| Dead-letter queue | Not formalized |
| Real marketplace HTML | **Out of scope** without permitted API/ToS |

**Recommendation:** Keep books.toscrape as the only live HTML source; add **API adapters** when keys exist. Do not expand illegal scraping for 2.0.

---

## 7. Frontend audit

**Components:** Dashboard, ProductDetail, Alerts, Competitors, MarketGrid, Auth, Settings, TrackProduct, UpgradePlan, etc.

**Issues**
- `frontend/src/data/mockData.ts` still seeds Sony/etc. UI narratives — conflicts with “real observations only” product story.
- API client exists (`api/products.ts` with getProductPrices, triggerScrape) but UI may still prefer mocks for charts/AI copy.
- Hybrid Vite + leftover Next artifacts in tree → clarify single build path.

**2.0 UI gap:** No first-class conversational AI analyst page wired to tool-calling backend.

---

## 8. Security report

| Control | Status |
|---------|--------|
| bcrypt passwords | Yes |
| JWT access tokens | Yes |
| Production SECRET_KEY / no SQLite / no CORS `*` | Fail-fast validation |
| Stripe webhook signature | Implemented when configured |
| Rate limits (login/register/products/scrape) | Redis fixed-window, fail-open |
| Object-level auth on products/alerts | Yes in mounted paths |
| IDOR tests | Cross-user product test present |
| Admin routes unmounted | Reduces exposure for now |
| Refresh tokens / RBAC enforcement | Weak / incomplete |
| Secrets in logs | Avoid; structured access log is OK if no tokens |

**Priority fixes:** Ensure orphan async admin routes never mount without authZ; document fail-open rate-limit policy; no secrets in client bundles.

---

## 9. Infrastructure & CI

| Item | Status |
|------|--------|
| docker-compose dev/prod | Present |
| Migrate service pattern | Documented in prod compose |
| Health live/ready | Yes |
| Metrics process counters | Yes |
| Request ID middleware | Yes |
| CI: pytest backend + scraper + Alembic on Postgres + frontend tsc/build | Yes |
| smoke_test.py | Added 2026-10-30 |
| Public production deploy | Not verified |

---

## 10. Technical debt (ranked)

| # | Debt | Impact | Sprint |
|---|------|--------|--------|
| 1 | Dual API stacks (`intelligence` sync vs `analytics`/`ai` async) | Confusion, double maintenance | 1 |
| 2 | Unmounted routers with advanced features | Docs over-claim vs runtime | 1 |
| 3 | Frontend mockData vs real API | Demo lies | 1–2 |
| 4 | Alembic incomplete vs models | Prod schema risk | 1 |
| 5 | No formal ScrapingJob/DLQ | Ops blindness | 2 |
| 6 | Matching without variant rules / embeddings | False matches | 3 |
| 7 | Insights not true tool-calling LLM | 2.0 flagship missing | 5 |
| 8 | Forecast not evaluated/mounted | Resume risk if claimed | 6 |

---

## 11. Enhancement backlog (aligned to 2.0 phases)

### P0 — before new AI features
1. Single session strategy (sync **or** async end-to-end).
2. Mount **one** analytics/intelligence surface; delete or merge duplicates.
3. Alembic revision that matches all live models.
4. Frontend: kill mock product intelligence paths for demo account.
5. Observation uniqueness / scrape job table (minimal).

### P1 — core 2.0
6. LLM tool-calling analyst (authorized tools only, user-scoped).
7. Alert delivery + dedupe store.
8. Hybrid matching + variant attributes.
9. E2E tests for register → scrape → history → alert → insight.

### P2
10. pgvector semantic match (only if fuzzy baseline measured).
11. Forecast with baseline comparison + “experimental” label.
12. Email notifications.

### P3
13. K8s / multi-region — not needed for placement demo.

---

## 12. Sprint 0 completion checklist

- [x] Map mounted vs unmounted APIs  
- [x] List models and migration risk  
- [x] Scraper allowed-source posture  
- [x] Security controls inventory  
- [x] Frontend mock vs API risk  
- [x] CI/CD presence  
- [x] Ranked debt + backlog  
- [ ] Run full pytest + smoke against live Postgres (operator machine)  
- [ ] Confirm production URL if any  

---

## 13. Recommended Sprint 1 kickoff (next)

1. **Decision record:** “Sync SQLAlchemy is source of truth for HTTP handlers until full async migration is funded.”  
2. Merge useful endpoints from `analytics.py` / `ai.py` into mounted sync routers **or** implement real AsyncSession and mount them — pick one.  
3. Generate Alembic migration from current models; test upgrade/downgrade on Postgres.  
4. Replace frontend mock catalog with books.toscrape-backed API data for default demo.  
5. Add `ScrapingJob` status fields only if needed for observability (avoid model explosion).

**Do not start Gemini/OpenAI tool-calling until (1)–(4) are green.**

---

*Audit method: static review of GitHub `main` tree downloaded 2026-10-31; runtime Docker build not executed in this environment.*
