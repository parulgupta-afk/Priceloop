from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.alert import AlertRuleType
from app.models.product import Product
from app.models.user import User
from app.services.alert_service import create_alert, evaluate_alerts_for_product, list_alerts
from app.services.insight_service import generate_insight
from app.services.nl_query_service import answer_question

router = APIRouter(tags=["ai", "alerts"])


class NLQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    product_id: UUID | None = None


class AlertCreate(BaseModel):
    product_id: UUID | None = None
    rule_type: AlertRuleType
    threshold: float | None = None


async def _owned_product(product_id: UUID, user: User, db: AsyncSession) -> Product:
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/{product_id}/insights")
async def get_insight(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _owned_product(product_id, current_user, db)
    return await generate_insight(db, product_id)


@router.post("/ai/query")
async def nl_query(
    body: NLQueryRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if body.product_id:
        await _owned_product(body.product_id, current_user, db)
    return await answer_question(db, body.product_id, body.question)


@router.get("/alerts")
async def get_alerts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    alerts = await list_alerts(db, current_user.id)
    return [
        {
            "id": str(a.id),
            "product_id": str(a.product_id) if a.product_id else None,
            "rule_type": a.rule_type.value,
            "threshold": a.threshold,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.post("/alerts", status_code=201)
async def post_alert(
    body: AlertCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if body.product_id:
        await _owned_product(body.product_id, current_user, db)
    alert = await create_alert(
        db,
        user_id=current_user.id,
        rule_type=body.rule_type,
        product_id=body.product_id,
        threshold=body.threshold,
    )
    return {
        "id": str(alert.id),
        "rule_type": alert.rule_type.value,
        "threshold": alert.threshold,
        "product_id": str(alert.product_id) if alert.product_id else None,
    }


@router.post("/products/{product_id}/alerts/evaluate")
async def evaluate_product_alerts(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _owned_product(product_id, current_user, db)
    triggered = await evaluate_alerts_for_product(db, product_id, current_user.id)
    return {"product_id": str(product_id), "triggered": triggered}
