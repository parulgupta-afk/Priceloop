"""
Statistical anomaly detection on price observations (sync).
Baseline: z-score, IQR, % deviation, and median absolute deviation (MAD).
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import PriceObservation, ProductListing


def _z_score_indices(prices: list[float], threshold: float = 2.5) -> list[int]:
    if len(prices) < 5:
        return []
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
    std = variance ** 0.5
    if std == 0:
        return []
    return [i for i, p in enumerate(prices) if abs((p - mean) / std) > threshold]


def _iqr_indices(prices: list[float], k: float = 1.5) -> list[int]:
    if len(prices) < 5:
        return []
    sorted_p = sorted(prices)
    n = len(sorted_p)
    q1 = sorted_p[n // 4]
    q3 = sorted_p[(3 * n) // 4]
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return [i for i, p in enumerate(prices) if p < lower or p > upper]


def _pct_indices(prices: list[float], window: int = 5, threshold_pct: float = 15.0) -> list[int]:
    if len(prices) < window + 1:
        return []
    out = []
    for i in range(window, len(prices)):
        recent = prices[i - window : i]
        rm = sum(recent) / len(recent)
        if rm == 0:
            continue
        if abs((prices[i] - rm) / rm) * 100 >= threshold_pct:
            out.append(i)
    return out


def _mad_indices(prices: list[float], threshold: float = 3.5) -> list[int]:
    """Robust anomaly score via median absolute deviation."""
    if len(prices) < 5:
        return []
    med = median(prices)
    abs_dev = [abs(p - med) for p in prices]
    mad = median(abs_dev)
    if mad == 0:
        # all equal or near-equal — only flag exact extremes if any non-median
        return [i for i, p in enumerate(prices) if p != med]
    # consistent with normal: scale MAD by 1.4826
    scale = 1.4826 * mad
    return [i for i, p in enumerate(prices) if abs(p - med) / scale > threshold]


def detect_price_anomalies(
    db: Session,
    product_id: UUID,
    days: int = 60,
    methods: list[str] | None = None,
) -> dict[str, Any]:
    methods = methods or ["zscore", "iqr", "pct", "mad"]
    days = max(7, min(days, 365))
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    observations = (
        db.query(PriceObservation)
        .join(ProductListing)
        .filter(ProductListing.product_id == product_id, PriceObservation.scraped_at >= cutoff)
        .order_by(PriceObservation.scraped_at.asc())
        .all()
    )
    if len(observations) < 5:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": len(observations),
            "anomalies": [],
            "message": "Need at least 5 observations for reliable anomaly detection",
        }
    prices = [float(o.price) for o in observations]
    hits: dict[int, set[str]] = {}
    detectors = {
        "zscore": lambda: _z_score_indices(prices),
        "iqr": lambda: _iqr_indices(prices),
        "pct": lambda: _pct_indices(prices),
        "mad": lambda: _mad_indices(prices),
    }
    for name in methods:
        fn = detectors.get(name)
        if not fn:
            continue
        for i in fn():
            hits.setdefault(i, set()).add(name)
    anomalies = []
    for i, methods_hit in sorted(hits.items()):
        o = observations[i]
        anomalies.append({
            "observation_id": str(o.id),
            "price": float(o.price),
            "currency": o.currency,
            "scraped_at": o.scraped_at.isoformat() if o.scraped_at else None,
            "methods": sorted(methods_hit),
            "confidence": "high" if len(methods_hit) >= 2 else "medium",
        })
    return {
        "product_id": str(product_id),
        "window_days": days,
        "observation_count": len(observations),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "methods_used": methods,
        "note": "Anomaly does not prove a deal or error; validate product identity and source quality.",
    }
