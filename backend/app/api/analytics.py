from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.product import Product
from app.models.user import User
from app.services.analytics_service import get_competitor_snapshot, get_product_analytics
from app.services.matching_service import create_match, find_potential_matches

router = APIRouter(tags=["analytics", "matching"])


async def _get_owned_product(
    product_id: UUID, user: User, db: AsyncSession
) -> Product:
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/{product_id}/analytics")
async def product_analytics(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=1, le=365),
):
    await _get_owned_product(product_id, current_user, db)
    return await get_product_analytics(db, product_id, days=days)


@router.get("/products/{product_id}/competitors")
async def product_competitors(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _get_owned_product(product_id, current_user, db)
    return await get_competitor_snapshot(db, product_id)


@router.get("/products/{product_id}/matches")
async def suggest_matches(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    min_confidence: float = Query(0.60, ge=0.0, le=1.0),
):
    await _get_owned_product(product_id, current_user, db)
    matches = await find_potential_matches(
        db, product_id, min_confidence=min_confidence
    )
    return {"product_id": str(product_id), "potential_matches": matches}


@router.post("/products/{product_id}/matches/{other_id}")
async def confirm_match(
    product_id: UUID,
    other_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    confidence: float = Query(0.95, ge=0.0, le=1.0),
):
    """Manually confirm that two products are the same."""
    await _get_owned_product(product_id, current_user, db)
    await _get_owned_product(other_id, current_user, db)

    match = await create_match(
        db,
        product_a_id=product_id,
        product_b_id=other_id,
        confidence=confidence,
        method="manual",
        reviewed=True,
        is_confirmed=True,
    )
    return {
        "id": str(match.id),
        "product_a_id": str(match.product_a_id),
        "product_b_id": str(match.product_b_id),
        "confidence": match.confidence,
        "is_confirmed": match.is_confirmed,
    }


# ---------------------------------------------------------------------------
# Anomaly Detection & Forecasting
# ---------------------------------------------------------------------------

from app.services.anomaly_service import detect_price_anomalies
from app.services.forecast_service import forecast_price


@router.get("/products/{product_id}/anomalies")
async def product_anomalies(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(60, ge=7, le=365),
):
    await _get_owned_product(product_id, current_user, db)
    return await detect_price_anomalies(db, product_id, days=days)


@router.get("/products/{product_id}/forecast")
async def product_forecast(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    horizon_days: int = Query(7, ge=1, le=30),
    history_days: int = Query(60, ge=7, le=365),
):
    await _get_owned_product(product_id, current_user, db)
    return await forecast_price(
        db, product_id, horizon_days=horizon_days, history_days=history_days
    )


from app.services.analytics_service import get_product_intelligence_summary


@router.get("/products/{product_id}/summary")
async def product_intelligence_summary(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=1, le=365),
):
    """Dashboard-ready combined view of analytics + competitive position."""
    await _get_owned_product(product_id, current_user, db)
    return await get_product_intelligence_summary(db, product_id, days=days)
