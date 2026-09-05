import json

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, billing, products
from app.core.config import settings
from app.core.database import engine
from app.models import product, subscription, user  # noqa: F401 - ensures models are registered
from app.models.base import Base

app = FastAPI(title="Priceloop", version="0.1.0")

# CORS: the frontend is deployed on its own origin (e.g. a Vercel domain),
# so without this every browser request to the API is blocked. Configure
# CORS_ORIGINS as a comma-separated env var in production instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])


@app.on_event("startup")
def on_startup():
    if settings.environment == "production" and settings.secret_key == "change-me":
        # Fail loudly rather than silently issuing forgeable JWTs in production.
        raise RuntimeError(
            "SECRET_KEY is still the default 'change-me' value. "
            "Set a real SECRET_KEY in the environment before running in production."
        )
    if settings.environment == "production":
        # Production schema is managed by Alembic (see backend/alembic/), run
        # once by a dedicated migrate step before this container starts --
        # see docker-compose.prod.yml. Running create_all() here too would
        # create tables Alembic doesn't know about, and the two can drift.
        pass
    else:
        # Local dev / tests: just create whatever's missing, no migration
        # ceremony needed for quick iteration.
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    """Kept for backwards compatibility -- prefer /health/live and
    /health/ready below, which distinguish "process is up" from
    "dependencies are reachable"."""
    return {"status": "ok"}


@app.get("/health/live")
def health_live():
    """Liveness: is the process itself up? Deliberately checks nothing
    external -- if this is slow or fails, the answer should be "restart the
    container," not "wait on the database.\""""
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Readiness: can this instance actually serve traffic right now?
    Checks the dependencies real requests need -- Postgres and Redis.
    Kept cheap (a trivial query / PING), not a full data validation pass."""
    import redis as redis_client

    checks = {"database": False, "redis": False}

    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False

    try:
        r = redis_client.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False

    all_ok = all(checks.values())
    return Response(
        content=json.dumps({"status": "ok" if all_ok else "unavailable", "checks": checks}),
        media_type="application/json",
        status_code=200 if all_ok else 503,
    )
