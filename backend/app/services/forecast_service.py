"""
Experimental short-horizon price forecasting from stored observations.
Baselines: last value, moving average, exponential smoothing + simple trend.
Always labeled experimental — not financial advice.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from statistics import pstdev
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import PriceObservation, ProductListing


def _moving_average(prices: list[float], window: int = 7) -> float | None:
    if not prices:
        return None
    window = min(window, len(prices))
    return sum(prices[-window:]) / window


def _exponential_smoothing(prices: list[float], alpha: float = 0.3) -> float | None:
    if not prices:
        return None
    level = prices[0]
    for p in prices[1:]:
        level = alpha * p + (1 - alpha) * level
    return level


def _simple_trend(prices: list[float]) -> float:
    n = len(prices)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(prices) / n
    num = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n)) or 1.0
    return num / den


def forecast_product_price(
    db: Session,
    product_id: UUID,
    horizon_days: int = 7,
    history_days: int = 90,
) -> dict[str, Any]:
    horizon_days = max(1, min(horizon_days, 30))
    history_days = max(14, min(history_days, 365))
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=history_days)
    rows = (
        db.query(PriceObservation)
        .join(ProductListing)
        .filter(ProductListing.product_id == product_id, PriceObservation.scraped_at >= cutoff)
        .order_by(PriceObservation.scraped_at.asc())
        .all()
    )
    if len(rows) < 5:
        return {
            "product_id": str(product_id),
            "forecast_horizon_days": horizon_days,
            "status": "insufficient_data",
            "observation_count": len(rows),
            "confidence": "none",
            "label": "experimental",
            "message": "Need at least 5 observations for experimental forecast.",
        }
    prices = [float(o.price) for o in rows]
    currency = rows[-1].currency
    last = prices[-1]
    ma = _moving_average(prices, 7) or last
    es = _exponential_smoothing(prices) or last
    trend = _simple_trend(prices)
    predicted = es + trend * horizon_days
    try:
        sigma = pstdev(prices[-min(14, len(prices)):]) if len(prices) >= 2 else abs(last) * 0.05
    except Exception:
        sigma = abs(last) * 0.05
    lower = max(0.0, predicted - 1.64 * sigma)
    upper = predicted + 1.64 * sigma
    return {
        "product_id": str(product_id),
        "forecast_horizon_days": horizon_days,
        "history_days": history_days,
        "observation_count": len(rows),
        "currency": currency,
        "last_price": round(last, 4),
        "predicted_point": round(predicted, 4),
        "predicted_price_range": {"lower": round(lower, 4), "upper": round(upper, 4)},
        "baselines": {
            "last_value": round(last, 4),
            "moving_average_7": round(ma, 4),
            "exponential_smoothing": round(es, 4),
        },
        "model": "exponential_smoothing_plus_trend",
        "confidence": "low" if len(rows) < 15 else "experimental",
        "label": "experimental",
        "disclaimer": "Experimental estimate from historical observations only. Not financial or pricing advice.",
    }
