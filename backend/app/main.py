from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, billing, products
from app.core.config import settings
from app.core.database import engine
from app.models import product, subscription, user  # noqa: F401 - ensures models are registered
from app.models.base import Base

app = FastAPI(title="Priceloop", version="0.1.0")

# CORS: the frontend is deployed on its own origin (e.g. a Vercel domain),
# so without this every browser request to the API is blocked. Configure
# ALLOWED_ORIGINS as a comma-separated env var in production instead of "*".
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
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
