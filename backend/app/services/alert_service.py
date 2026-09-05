"""
Smart alert rule engine (foundation).
Evaluates simple threshold rules against latest analytics / anomalies.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertEvent, AlertRuleType, AlertSeverity
from app.models.product import Product
from app.services.analytics_service import get_product_analytics
from app.services.anomaly_service import detect_price_anomalies


async def create_alert(
    db: AsyncSession,
    user_id: UUID,
    rule_type: AlertRuleType,
    product_id: UUID | None = None,
    threshold: float | None = None,
    channels: dict | None = None,
) -> Alert:
    alert = Alert(
        user_id=user_id,
        product_id=product_id,
        rule_type=rule_type,
        threshold=threshold,
        channels=channels or {"in_app": True},
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def list_alerts(db: AsyncSession, user_id: UUID) -> list[Alert]:
    result = await db.execute(
        select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
    )
    return list(result.scalars().all())


async def evaluate_alerts_for_product(
    db: AsyncSession, product_id: UUID, user_id: UUID
) -> list[dict[str, Any]]:
    """
    Run active alerts that target this product (or global ones)
    and create AlertEvent rows when rules fire.
    """
    result = await db.execute(
        select(Alert).where(
            Alert.user_id == user_id,
            Alert.is_active == True,
            (Alert.product_id == product_id) | (Alert.product_id.is_(None)),
        )
    )
    alerts = list(result.scalars().all())
    if not alerts:
        return []

    analytics = await get_product_analytics(db, product_id, days=30)
    anomalies = await detect_price_anomalies(db, product_id, days=30)

    triggered = []
    change = analytics.get("price_change_pct")
    anomaly_count = anomalies.get("anomaly_count", 0)

    for alert in alerts:
        fire = False
        severity = AlertSeverity.INFO
        message = ""

        if alert.rule_type == AlertRuleType.PRICE_DROP_PCT and change is not None:
            thresh = alert.threshold or 10.0
            if change <= -abs(thresh):
                fire = True
                severity = AlertSeverity.HIGH if abs(change) >= 15 else AlertSeverity.WARNING
                message = f"Price dropped {abs(change)}% (threshold {thresh}%)."

        elif alert.rule_type == AlertRuleType.PRICE_INCREASE_PCT and change is not None:
            thresh = alert.threshold or 10.0
            if change >= abs(thresh):
                fire = True
                severity = AlertSeverity.WARNING
                message = f"Price increased {change}% (threshold {thresh}%)."

        elif alert.rule_type == AlertRuleType.ANOMALY and anomaly_count > 0:
            fire = True
            severity = AlertSeverity.HIGH
            message = f"{anomaly_count} price anomal{'y' if anomaly_count == 1 else 'ies'} detected."

        if fire:
            event = AlertEvent(
                alert_id=alert.id,
                severity=severity,
                message=message,
                payload={
                    "product_id": str(product_id),
                    "change_pct": change,
                    "anomaly_count": anomaly_count,
                },
            )
            db.add(event)
            triggered.append(
                {
                    "alert_id": str(alert.id),
                    "rule_type": alert.rule_type.value,
                    "severity": severity.value,
                    "message": message,
                }
            )

    await db.flush()
    return triggered
