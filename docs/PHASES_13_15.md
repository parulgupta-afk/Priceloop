# Phases 13 – 15 Summary

## Phase 13 — Scraper Health & Observability (Completed)

- Models: `ScrapeJob`, `ScrapeResult`
- `health_service.py`
  - Success / failure counts
  - Success rate %
  - Average duration
  - Per-source breakdown
  - Pending self-healing proposals count
- Scrape path now records a SUCCESS job (observability without breaking the main flow)
- Endpoint (Admin/Analyst):
  - `GET /api/v1/admin/scrapers/health?hours=24`

## Phase 14 — Self-Healing Selectors (Foundation, human-in-the-loop)

- Model: `SelectorProposal`
- `self_healing_service.py`
  - Create proposal
  - List pending proposals
  - Approve / Reject (records reviewer + timestamp)
  - Mock AI selector suggestion (offline-safe)
- **Critical design rule**: proposals stay `PENDING` until an Admin explicitly approves. No silent production changes.
- Endpoints:
  - `GET  /api/v1/admin/selectors/proposals`
  - `POST /api/v1/admin/selectors/proposals`
  - `POST /api/v1/admin/selectors/proposals/{id}/review?approve=true|false`
  - `POST /api/v1/admin/selectors/suggest` (demo mock AI)

## Phase 15 — Cost Intelligence (Foundation)

- Model: `CostRecord`
- `cost_service.py` – record costs + category summary
- Endpoints:
  - `GET  /api/v1/admin/costs`
  - `POST /api/v1/admin/costs`

Useful for the portfolio FinOps story (“we track X SKUs at ₹Y/month”).

---

## Admin API surface (this batch)

| Method | Path | Role | Purpose |
|--------|------|------|---------|
| GET | `/api/v1/admin/scrapers/health` | Admin/Analyst | Scraper health dashboard data |
| GET | `/api/v1/admin/selectors/proposals` | Admin | List selector proposals |
| POST | `/api/v1/admin/selectors/proposals` | Admin | Create proposal |
| POST | `/api/v1/admin/selectors/proposals/{id}/review` | Admin | Approve/reject |
| POST | `/api/v1/admin/selectors/suggest` | Admin | Mock AI suggestion |
| GET | `/api/v1/admin/costs` | Admin/Analyst | Cost summary |
| POST | `/api/v1/admin/costs` | Admin | Record a cost |

---

## Design notes

- Observability never breaks the main scrape path.
- Self-healing is intentionally **human-gated**.
- Cost tracking is simple but enough to tell a clear infrastructure story in interviews.
