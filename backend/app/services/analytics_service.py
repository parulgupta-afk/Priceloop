"""
Price history metrics — deterministic, based only on stored observations.
Sync Session version (matches rest of API stack).
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from statistics import mean, median
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import PriceObservation, ProductListing


def _pct_change(old: float | None, new: float | None) -> float | None:
    if old is None or new is None or old == 0:
        return None
    return round(((new - old) / old) * 100, 2)


def get_product_analytics(db: Session, product_id: UUID, days: int = 30) -> dict[str, Any]:
    days = max(1, min(days, 365))
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    observations = (
        db.query(PriceObservation)
        .join(ProductListing)
        .filter(
            ProductListing.product_id == product_id,
            PriceObservation.scraped_at >= cutoff,
        )
        .order_by(PriceObservation.scraped_at.asc())
        .all()
    )
    if not observations:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": 0,
            "message": "No price observations in the selected window",
        }
    prices = [float(o.price) for o in observations if o.price is not None]
    if not prices:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": len(observations),
            "message": "Observations exist but no valid prices",
        }
    current = prices[-1]
    previous = prices[-2] if len(prices) > 1 else None
    min_p = min(prices)
    max_p = max(prices)
    avg_p = mean(prices)
    med_p = median(prices)
    volatility = None
    if len(prices) > 1 and avg_p > 0:
        variance = sum((p - avg_p) ** 2 for p in prices) / (len(prices) - 1)
        std = variance ** 0.5
        volatility = round(std / avg_p, 4)
    return {
        "product_id": str(product_id),
        "window_days": days,
        "observation_count": len(observations),
        "current_price": current,
        "previous_price": previous,
        "absolute_change": None if previous is None else round(current - previous, 2),
        "percent_change": _pct_change(previous, current),
        "min_price": min_p,
        "max_price": max_p,
        "avg_price": round(avg_p, 2),
        "median_price": round(med_p, 2),
        "volatility": volatility,
        "currency": observations[-1].currency if observations else None,
        "first_observed_at": observations[0].scraped_at.isoformat() if observations else None,
        "last_observed_at": observations[-1].scraped_at.isoformat() if observations else None,
    }
