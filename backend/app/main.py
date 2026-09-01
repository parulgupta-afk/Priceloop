from fastapi import FastAPI

from app.api import auth, products
from app.core.database import engine
from app.models import product, user  # noqa: F401 - ensures models are registered
from app.models.base import Base

app = FastAPI(title="Priceloop", version="0.1.0")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
