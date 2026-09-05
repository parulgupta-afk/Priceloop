"""
Statistical anomaly detection on price time-series.
Starts with classic methods (z-score, IQR, percentage deviation).
Later can be upgraded to isolation forest / LSTM autoencoders.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import PriceObservation, ProductListing


def _z_score_anomalies(prices: list[float], threshold: float = 2.5) -> list[int]:
    """Return indices where |z| > threshold."""
    if len(prices) < 5:
        return []
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
    std = variance ** 0.5
    if std == 0:
        return []
    return [i for i, p in enumerate(prices) if abs((p - mean) / std) > threshold]


def _iqr_anomalies(prices: list[float], k: float = 1.5) -> list[int]:
    """Return indices outside [Q1 - k*IQR, Q3 + k*IQR]."""
    if len(prices) < 5:
        return []
    sorted_p = sorted(prices)
    n = len(sorted_p)
    q1 = sorted_p[n // 4]
    q3 = sorted_p[(3 * n) // 4]
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return [i for i, p in enumerate(prices) if p < lower or p > upper]


def _pct_deviation_anomalies(
    prices: list[float], window: int = 5, threshold_pct: float = 15.0
) -> list[int]:
    """Flag points that deviate > threshold_pct from the recent rolling mean."""
    if len(prices) < window + 1:
        return []
    anomalies = []
    for i in range(window, len(prices)):
        recent = prices[i - window : i]
        rolling_mean = sum(recent) / len(recent)
        if rolling_mean == 0:
            continue
        pct = abs((prices[i] - rolling_mean) / rolling_mean) * 100
        if pct >= threshold_pct:
            anomalies.append(i)
    return anomalies


async def detect_price_anomalies(
    db: AsyncSession,
    product_id: UUID,
    days: int = 60,
    methods: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run multiple statistical detectors and return a unified list of anomalies.
    """
    if methods is None:
        methods = ["zscore", "iqr", "pct"]

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
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

    if len(observations) < 5:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": len(observations),
            "anomalies": [],
            "message": "Not enough observations for reliable anomaly detection (need ≥ 5)",
        }

    prices = [float(o.price) for o in observations]
    timestamps = [o.scraped_at.isoformat() for o in observations]
    obs_ids = [str(o.id) for o in observations]

    flagged: dict[int, set[str]] = {}

    if "zscore" in methods:
        for idx in _z_score_anomalies(prices):
            flagged.setdefault(idx, set()).add("zscore")
    if "iqr" in methods:
        for idx in _iqr_anomalies(prices):
            flagged.setdefault(idx, set()).add("iqr")
    if "pct" in methods:
        for idx in _pct_deviation_anomalies(prices):
            flagged.setdefault(idx, set()).add("pct_deviation")

    anomalies = []
    for idx, detectors in sorted(flagged.items()):
        direction = "DROP" if idx > 0 and prices[idx] < prices[idx - 1] else "SPIKE"
        if idx > 0:
            change_pct = round(
                ((prices[idx] - prices[idx - 1]) / prices[idx - 1]) * 100, 2
            )
        else:
            change_pct = None

        severity = "HIGH" if len(detectors) >= 2 else "MEDIUM"
        anomalies.append(
            {
                "observation_id": obs_ids[idx],
                "timestamp": timestamps[idx],
                "price": prices[idx],
                "previous_price": prices[idx - 1] if idx > 0 else None,
                "change_pct": change_pct,
                "direction": direction,
                "severity": severity,
                "detected_by": sorted(detectors),
            }
        )

    return {
        "product_id": str(product_id),
        "window_days": days,
        "observation_count": len(observations),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "methods_used": methods,
    }
