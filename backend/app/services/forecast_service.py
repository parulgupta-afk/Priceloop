"""
Simple short-term price forecasting.
Starts with Moving Average + Exponential Smoothing.
Later: XGBoost / Prophet / LSTM.
Always returns a confidence interval / uncertainty measure.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import PriceObservation, ProductListing


def _moving_average(prices: list[float], window: int = 7) -> float | None:
    if len(prices) < window:
        window = len(prices)
    if window == 0:
        return None
    return sum(prices[-window:]) / window


def _exponential_smoothing(prices: list[float], alpha: float = 0.3) -> float | None:
    if not prices:
        return None
    level = prices[0]
    for p in prices[1:]:
        level = alpha * p + (1 - alpha) * level
    return level


def _simple_trend(prices: list[float]) -> float:
    """Very rough linear slope (price units per observation)."""
    n = len(prices)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(prices) / n
    num = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


async def forecast_price(
    db: AsyncSession,
    product_id: UUID,
    horizon_days: int = 7,
    history_days: int = 60,
) -> dict[str, Any]:
    """
    Produce a short-term forecast with a confidence band.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=history_days)
    result = await db.execute(
        select(PriceObservation)
        .join(ProductListing)
        .where(
            ProductListing.product_id == product_id,
            PriceObservation.scraped_at >= cutoff,
        )
        .order_by(PriceObservation.scraped_at.asc())
    )
    observations = list(result.scalars().all())

    if len(observations) < 3:
        return {
            "product_id": str(product_id),
            "horizon_days": horizon_days,
            "message": "Not enough history to forecast (need ≥ 3 observations)",
            "forecast": None,
        }

    prices = [float(o.price) for o in observations]
    current = prices[-1]
    currency = observations[-1].currency

    ma = _moving_average(prices, window=min(7, len(prices)))
    es = _exponential_smoothing(prices)
    trend = _simple_trend(prices[-14:] if len(prices) >= 14 else prices)

    # Blend for the point forecast
    point = None
    if ma is not None and es is not None:
        point = 0.5 * ma + 0.5 * es + trend * (horizon_days / 2)
    elif es is not None:
        point = es + trend * (horizon_days / 2)
    else:
        point = current

    point = round(point, 2)

    # Simple uncertainty band based on recent volatility
    recent = prices[-14:] if len(prices) >= 14 else prices
    mean_r = sum(recent) / len(recent)
    if len(recent) > 1 and mean_r > 0:
        variance = sum((p - mean_r) ** 2 for p in recent) / (len(recent) - 1)
        std = variance ** 0.5
        # Widen the band a bit for longer horizons
        band = std * (1 + 0.1 * horizon_days)
    else:
        band = current * 0.03  # 3% fallback

    low = round(max(0, point - band), 2)
    high = round(point + band, 2)

    # Direction label
    if point < current * 0.98:
        direction = "Likely Down"
    elif point > current * 1.02:
        direction = "Likely Up"
    else:
        direction = "Likely Stable"

    # Confidence heuristic (more data + lower volatility → higher confidence)
    data_factor = min(len(prices) / 30, 1.0)
    vol_factor = max(0.0, 1.0 - (band / current if current else 1))
    confidence = round(0.4 * data_factor + 0.6 * vol_factor, 2)
    confidence = max(0.35, min(0.92, confidence))

    return {
        "product_id": str(product_id),
        "horizon_days": horizon_days,
        "history_days": history_days,
        "observation_count": len(observations),
        "current_price": current,
        "currency": currency,
        "forecast": {
            "point": point,
            "low": low,
            "high": high,
            "direction": direction,
            "confidence": confidence,
        },
        "methods": ["moving_average", "exponential_smoothing", "linear_trend"],
        "note": "Probabilistic estimate only. Not financial advice.",
    }
