"""Price history, analytics, and manual scrape trigger (sync)."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rate_limit import limit_products_read, limit_scrape_trigger
from app.core.cache import cache_get, cache_set, prices_key, analytics_key, cache_delete_prefix, DEFAULT_TTL_PRICES, DEFAULT_TTL_ANALYTICS
from app.models.product import PriceObservation, Product, ProductListing
from app.models.user import User
from app.schemas.product import PriceObservationOut
from app.services.scrape_service import scrape_listing
from app.services.analytics_service import get_product_analytics

router = APIRouter(tags=["prices"])


@router.get("/products/{product_id}/prices", response_model=List[PriceObservationOut], dependencies=[Depends(limit_products_read)])
def get_product_prices(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100,
):
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    limit = max(1, min(limit, 500))
    ck = prices_key(str(product_id), limit)
    cached = cache_get(ck)
    if cached is not None:
        return cached
    observations = (
        db.query(PriceObservation)
        .join(ProductListing)
        .filter(ProductListing.product_id == product_id)
        .order_by(PriceObservation.scraped_at.desc())
        .limit(limit)
        .all()
    )
    out = [
        {
            "id": str(o.id),
            "listing_id": str(o.listing_id),
            "price": float(o.price),
            "currency": o.currency,
            "availability": o.availability,
            "scraped_at": o.scraped_at.isoformat() if o.scraped_at else None,
        }
        for o in observations
    ]
    cache_set(ck, out, DEFAULT_TTL_PRICES)
    return observations


@router.get("/products/{product_id}/analytics", dependencies=[Depends(limit_products_read)])
def product_analytics(
    product_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ck = analytics_key(str(product_id), days)
    cached = cache_get(ck)
    if cached is not None:
        return cached
    data = get_product_analytics(db, product_id, days=days)
    cache_set(ck, data, DEFAULT_TTL_ANALYTICS)
    return data


@router.post("/listings/{listing_id}/scrape", response_model=PriceObservationOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(limit_scrape_trigger)])
def trigger_scrape(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = (
        db.query(ProductListing)
        .join(Product)
        .filter(ProductListing.id == listing_id, Product.user_id == current_user.id)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    try:
        observation = scrape_listing(db, listing_id)
        db.commit()
        db.refresh(observation)
        # invalidate caches for this product
        cache_delete_prefix(f"cache:prices:{listing.product_id}")
        cache_delete_prefix(f"cache:analytics:{listing.product_id}")
        cache_delete_prefix(f"cache:product:{listing.product_id}")
        return observation
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Scrape failed: {type(exc).__name__}") from exc
