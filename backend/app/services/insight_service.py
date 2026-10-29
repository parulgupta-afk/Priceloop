"""
Evidence-grounded market analyst.
Computes stats in code; optional LLM only explains structured evidence.
Never invents prices or causes without data.
"""
from __future__ import annotations
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.analytics_service import get_product_analytics
from app.services.anomaly_service import detect_price_anomalies
from app.core.config import settings


def build_evidence(db: Session, product_id: UUID, days: int = 30) -> dict[str, Any]:
    analytics = get_product_analytics(db, product_id, days=days)
    anomalies = detect_price_anomalies(db, product_id, days=max(days, 60))
    return {
        "analytics": analytics,
        "anomalies": {
            "count": anomalies.get("anomaly_count", 0),
            "items": anomalies.get("anomalies", [])[:5],
        },
        "window_days": days,
    }


def _rule_based_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    a = evidence.get("analytics") or {}
    obs = a.get("observation_count", 0)
    if obs == 0:
        return {
            "summary": "No price observations are available for the selected period.",
            "observations": [],
            "possible_explanations": [],
            "confidence": "none",
            "limitations": ["No historical price data stored yet."],
        }
    parts = []
    if a.get("current_price") is not None:
        parts.append(f"Latest observed price is {a.get('currency', '')} {a['current_price']}.")
    if a.get("percent_change") is not None:
        direction = "decreased" if a["percent_change"] < 0 else "increased"
        parts.append(f"It {direction} by {abs(a['percent_change'])}% versus the previous observation.")
    if a.get("min_price") is not None and a.get("max_price") is not None:
        parts.append(f"In the window, observed range was {a['min_price']}–{a['max_price']}.")
    an_count = evidence.get("anomalies", {}).get("count", 0)
    if an_count:
        parts.append(f"{an_count} statistical anomal(ies) were flagged; this is not proof of a promotion or error.")
    observations = []
    for key in ("current_price", "previous_price", "percent_change", "min_price", "max_price", "avg_price"):
        if a.get(key) is not None:
            observations.append({"metric": key, "value": a[key]})
    return {
        "summary": " ".join(parts) if parts else "Price data exists but changes could not be summarized.",
        "observations": observations,
        "possible_explanations": [
            "Genuine market price change",
            "Temporary listing or currency artifact",
            "Insufficient history for strong inference",
        ],
        "confidence": "limited" if obs < 5 else "moderate",
        "limitations": [
            "Explanations are not causal claims.",
            "Only recorded PriceLoop observations were used.",
            "External events (competitor launches, sales) are unknown unless stored as data.",
        ],
    }


def generate_insight(db: Session, product_id: UUID, days: int = 30) -> dict[str, Any]:
    evidence = build_evidence(db, product_id, days=days)
    base = _rule_based_summary(evidence)
    base["evidence"] = {
        "observation_count": evidence.get("analytics", {}).get("observation_count"),
        "anomaly_count": evidence.get("anomalies", {}).get("count"),
        "window_days": days,
    }
    # Optional LLM polish — only if key configured; still constrained to evidence
    api_key = getattr(settings, "openai_api_key", "") or getattr(settings, "llm_api_key", "")
    if api_key:
        try:
            base["llm"] = "skipped_in_batch"  # keep offline-safe; wire provider later
        except Exception:
            pass
    base["model"] = "rule_based_v1"
    return base
