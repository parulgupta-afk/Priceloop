from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.product import PriceObservation, Product, ProductListing
from app.models.user import User
from app.schemas.product import PriceObservationOut
from app.services.scrape_service import scrape_listing

router = APIRouter(tags=["prices"])


@router.get(
    "/products/{product_id}/prices",
    response_model=list[PriceObservationOut],
)
async def get_product_prices(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 100,
) -> list[PriceObservation]:
    # Verify ownership
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    obs_result = await db.execute(
        select(PriceObservation)
        .join(ProductListing)
        .where(ProductListing.product_id == product_id)
        .order_by(PriceObservation.scraped_at.desc())
        .limit(limit)
    )
    return list(obs_result.scalars().all())


@router.post(
    "/listings/{listing_id}/scrape",
    response_model=PriceObservationOut,
    status_code=status.HTTP_201_CREATED,
)
async def trigger_scrape(
    listing_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PriceObservation:
    """Manually trigger a scrape for a listing (useful for development & demos)."""
    # Ownership check
    result = await db.execute(
        select(ProductListing)
        .join(Product)
        .where(
            ProductListing.id == listing_id,
            Product.user_id == current_user.id,
        )
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    try:
        observation = await scrape_listing(db, listing_id)
        return observation
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scrape failed: {exc}",
        ) from exc
