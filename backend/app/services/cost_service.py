"""
Cost intelligence – track approximate infrastructure spend.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraper_ops import CostRecord


async def record_cost(
    db: AsyncSession,
    category: str,
    amount: float,
    currency: str = "INR",
    source_name: str | None = None,
    units: float | None = None,
    meta: dict | None = None,
) -> CostRecord:
    rec = CostRecord(
        category=category,
        amount=amount,
        currency=currency,
        source_name=source_name,
        units=units,
        meta=meta,
        period_start=datetime.now(timezone.utc),
        period_end=datetime.now(timezone.utc),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return rec


async def cost_summary(db: AsyncSession) -> dict[str, Any]:
    result = await db.execute(
        select(
            CostRecord.category,
            func.sum(CostRecord.amount),
            func.count(),
        ).group_by(CostRecord.category)
    )
    rows = result.all()
    by_category = [
        {"category": cat, "total": float(total or 0), "records": count}
        for cat, total, count in rows
    ]
    grand = sum(item["total"] for item in by_category)
    return {
        "by_category": by_category,
        "grand_total": round(grand, 2),
        "currency": "INR",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
