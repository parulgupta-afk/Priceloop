"""Anomaly, matching, insights, alerts — Phases 8–11."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rate_limit import limit_products_read, rate_limit
from app.models.user import User
from app.services.anomaly_service import detect_price_anomalies
from app.services.matching_service import find_matches_for_product
from app.services.insight_service import generate_insight
from app.services import alert_service

router = APIRouter(tags=["intelligence"])
limit_ai = rate_limit(max_requests=10, window_seconds=60, prefix="ai", per_user=True)


class AlertCreate(BaseModel):
    product_id: UUID
    rule_type: str = Field(..., description="PRICE_DROP_PCT | PRICE_INCREASE_PCT | ANOMALY | OUT_OF_STOCK | ...")
    threshold: Optional[float] = None
    channels: Optional[dict] = None


class AlertOut(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    rule_type: str
    threshold: Optional[float]
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/products/{product_id}/anomalies", dependencies=[Depends(limit_products_read)])
def product_anomalies(
    product_id: UUID,
    days: int = Query(60, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.product import Product
    p = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return detect_price_anomalies(db, product_id, days=days)


@router.get("/products/{product_id}/matches", dependencies=[Depends(limit_products_read)])
def product_matches(
    product_id: UUID,
    min_score: float = Query(0.75, ge=0.5, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return find_matches_for_product(db, current_user.id, product_id, min_score=min_score)


@router.get("/products/{product_id}/insights", dependencies=[Depends(limit_ai)])
def product_insights(
    product_id: UUID,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.product import Product
    p = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return generate_insight(db, product_id, days=days)


@router.post("/alerts", response_model=AlertOut, dependencies=[Depends(limit_products_read)])
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return alert_service.create_alert(
        db, current_user.id, payload.product_id, payload.rule_type, payload.threshold, payload.channels
    )


@router.get("/alerts", response_model=List[AlertOut], dependencies=[Depends(limit_products_read)])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    active_only: bool = True,
):
    alerts = alert_service.list_alerts(db, current_user.id, active_only=active_only)
    return [
        AlertOut(
            id=a.id,
            product_id=a.product_id,
            rule_type=a.rule_type.value if hasattr(a.rule_type, "value") else str(a.rule_type),
            threshold=a.threshold,
            is_active=a.is_active,
        )
        for a in alerts
    ]


@router.delete("/alerts/{alert_id}", status_code=204, dependencies=[Depends(limit_products_read)])
def remove_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert_service.delete_alert(db, current_user.id, alert_id)
    return None


@router.post("/alerts/evaluate", dependencies=[Depends(limit_ai)])
def evaluate_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluate active alerts for the current user (dev/demo)."""
    return {"triggers": alert_service.evaluate_user_alerts(db, current_user.id)}
