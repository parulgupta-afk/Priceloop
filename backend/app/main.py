from fastapi import FastAPI

from app.api import auth, products

app = FastAPI(title="Priceloop", version="0.1.0")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])


@app.get("/health")
def health():
    return {"status": "ok"}
