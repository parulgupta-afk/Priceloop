# Security controls (Phase 9)

| Control | Status |
|---------|--------|
| bcrypt password hashing | Yes |
| JWT access tokens | Yes |
| Production SECRET_KEY strength check | Yes |
| Production forbids SQLite | Yes |
| Production forbids CORS `*` | Yes |
| Rate limits (auth, products, AI) | Redis fixed-window, fail-open |
| Object-level product/alert auth | Yes on mounted routes |
| Stripe webhook signature | When configured |
| Request IDs in access log | Yes |
| Orphan async admin routes | Not mounted |
| AI tools user-scoped | Yes — no raw SQL for model |

## Load testing
```bash
cd backend && python -m scripts.load_test --base http://localhost:8000 --users 5 --requests 30
```
Record measured p50/p95 — never invent numbers in README.
