# Deployment guide (Phase 15)

## Production compose

```bash
cp .env.example .env
# Required: SECRET_KEY (>=32), DATABASE_URL (postgres), REDIS_URL,
# STRIPE_* if billing, CORS_ORIGINS (no *)
docker compose -f docker-compose.prod.yml up --build -d
```

## Checklist

- [ ] `ENVIRONMENT=production`
- [ ] Strong `SECRET_KEY`
- [ ] Postgres not SQLite
- [ ] Redis reachable
- [ ] CORS explicit origins
- [ ] `alembic upgrade head` via migrate service
- [ ] `/health/live` and `/health/ready` on load balancer
- [ ] Stripe webhook URL + signature secret
- [ ] Logs collect stdout (request_id in access log)
- [ ] Backup Postgres volume

## Rollback

1. Redeploy previous image tag
2. `alembic downgrade -1` only if migration is reversible and tested
3. Verify `/health/ready`

## Observability

- `GET /health/live` — process up
- `GET /health/ready` — DB + Redis
- `GET /metrics` — uptime + counters
- Access logs include `request_id`, `path`, `status`, `duration_ms`
- Clients may send `X-Request-ID`; response echoes it


## Platform options (Phase 11)

| Component | Practical choice |
|-----------|------------------|
| Frontend | Vercel / Netlify (static Vite build) |
| API + worker | Render / Railway / Fly.io / single VM + Compose |
| PostgreSQL | Managed Postgres (required in production) |
| Redis | Managed Redis or Compose Redis |
| Migrations | One-shot `alembic upgrade head` before app start |

### Frontend build

```bash
cd frontend
VITE_API_URL=https://api.yourdomain.com/api npm run build
```

### Worker process

Run a second process with the same image:

```bash
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

### Smoke after deploy

```bash
curl -sf https://api.yourdomain.com/health/live
curl -sf https://api.yourdomain.com/health/ready
python -m scripts.smoke_test  # if configured against staging
```
