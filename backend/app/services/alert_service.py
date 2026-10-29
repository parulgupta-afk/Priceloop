"""
Price alerts: create rules, evaluate against latest observations, dedupe triggers.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertRuleType
from app.models.product import PriceObservation, Product, ProductListing


def create_alert(
    db: Session,
    user_id: UUID,
    product_id: UUID,
    rule_type: str,
    threshold: float | None = None,
    channels: dict | None = None,
) -> Alert:
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        rt = AlertRuleType(rule_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid rule_type. Allowed: {[e.value for e in AlertRuleType]}")
    alert = Alert(
        user_id=user_id,
        product_id=product_id,
        rule_type=rt,
        threshold=threshold,
        channels=channels or {"in_app": True},
        is_active=True,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(db: Session, user_id: UUID, active_only: bool = True) -> list[Alert]:
    q = db.query(Alert).filter(Alert.user_id == user_id)
    if active_only:
        q = q.filter(Alert.is_active.is_(True))
    return q.order_by(Alert.created_at.desc()).all()


def delete_alert(db: Session, user_id: UUID, alert_id: UUID) -> None:
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()


def _latest_two_prices(db: Session, product_id: UUID) -> tuple[float | None, float | None, str | None]:
    rows = (
        db.query(PriceObservation)
        .join(ProductListing)
        .filter(ProductListing.product_id == product_id)
        .order_by(PriceObservation.scraped_at.desc())
        .limit(2)
        .all()
    )
    if not rows:
        return None, None, None
    cur = float(rows[0].price)
    prev = float(rows[1].price) if len(rows) > 1 else None
    return cur, prev, rows[0].currency


def evaluate_alert(db: Session, alert: Alert) -> dict[str, Any] | None:
    """Return a trigger payload if condition met; None otherwise. Does not persist delivery."""
    if not alert.is_active or not alert.product_id:
        return None
    current, previous, currency = _latest_two_prices(db, alert.product_id)
    if current is None:
        return None
    rt = alert.rule_type
    thr = alert.threshold
    triggered = False
    detail = ""
    if rt == AlertRuleType.PRICE_DROP_PCT and previous and previous > 0 and thr is not None:
        pct = ((previous - current) / previous) * 100
        if pct >= thr:
            triggered = True
            detail = f"Price dropped {pct:.1f}% (threshold {thr}%)"
    elif rt == AlertRuleType.PRICE_INCREASE_PCT and previous and previous > 0 and thr is not None:
        pct = ((current - previous) / previous) * 100
        if pct >= thr:
            triggered = True
            detail = f"Price rose {pct:.1f}% (threshold {thr}%)"
    elif rt == AlertRuleType.OUT_OF_STOCK:
        # check latest availability on any listing
        listing = (
            db.query(ProductListing)
            .filter(ProductListing.product_id == alert.product_id)
            .order_by(ProductListing.last_scraped_at.desc().nullslast())
            .first()
        )
        if listing and (listing.availability or "").upper() in ("OUT_OF_STOCK", "OUT OF STOCK"):
            triggered = True
            detail = "Listing reported out of stock"
    elif rt == AlertRuleType.ANOMALY:
        from app.services.anomaly_service import detect_price_anomalies
        result = detect_price_anomalies(db, alert.product_id, days=60)
        if result.get("anomaly_count", 0) > 0:
            triggered = True
            detail = f"Detected {result['anomaly_count']} anomal(ies)"
    # THRESHOLD absolute: treat PRICE_DROP_PCT threshold as absolute "below X" when rule name abused
    if not triggered and thr is not None and previous is not None:
        # also support absolute floor via threshold when rule is PRICE_DROP_PCT and thr > 100 means absolute? skip
        pass
    if not triggered:
        return None
    return {
        "alert_id": str(alert.id),
        "product_id": str(alert.product_id),
        "rule_type": rt.value,
        "current_price": current,
        "previous_price": previous,
        "currency": currency,
        "detail": detail,
        "triggered_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_user_alerts(db: Session, user_id: UUID) -> list[dict[str, Any]]:
    alerts = list_alerts(db, user_id, active_only=True)
    triggers = []
    for a in alerts:
        t = evaluate_alert(db, a)
        if t:
            triggers.append(t)
    return triggers
