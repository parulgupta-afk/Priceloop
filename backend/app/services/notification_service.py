"""Alert evaluation with dedupe window."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from app.services.alert_service import list_alerts, evaluate_alert

_recent: dict[str, datetime] = {}
DEDUPE_MINUTES = 360


def evaluate_with_dedupe(db: Session, user_id: UUID) -> dict[str, Any]:
    triggers = []
    skipped = []
    now = datetime.now(timezone.utc)
    for alert in list_alerts(db, user_id, active_only=True):
        payload = evaluate_alert(db, alert)
        if not payload:
            continue
        key = f"{user_id}:{alert.id}:{(payload.get('detail') or '')[:80]}"
        last = _recent.get(key)
        if last and (now - last) < timedelta(minutes=DEDUPE_MINUTES):
            skipped.append({"alert_id": str(alert.id), "reason": "deduped"})
            continue
        _recent[key] = now
        triggers.append({"id": str(uuid4()), "channel": "in_app", "status": "delivered", **payload})
    return {
        "notifications": triggers,
        "deduped": skipped,
        "dedupe_window_minutes": DEDUPE_MINUTES,
    }
