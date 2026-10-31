"""
PriceLoop 2.0 — AI Market Analyst with authorized tool calling.

The LLM never gets raw SQL. Tools enforce user_id isolation.
If no API key is configured, a deterministic planner answers from tool results only.
"""
from __future__ import annotations
import re
from typing import Any, Callable
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import Product
from app.services.analytics_service import get_product_analytics
from app.services.anomaly_service import detect_price_anomalies
from app.services.matching_service import find_matches_for_product
from app.services.alert_service import list_alerts
from app.services.insight_service import generate_insight
from app.core.config import settings


def _owned_product(db: Session, user_id: UUID, product_id: UUID) -> Product | None:
    return db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()


def tool_list_products(db: Session, user_id: UUID, q: str | None = None, limit: int = 20) -> dict:
    query = db.query(Product).filter(Product.user_id == user_id)
    if q:
        query = query.filter(Product.name.ilike(f"%{q.strip()}%"))
    rows = query.order_by(Product.created_at.desc()).limit(min(limit, 50)).all()
    return {
        "products": [
            {"id": str(p.id), "name": p.name, "brand": p.brand, "category": p.category}
            for p in rows
        ],
        "count": len(rows),
    }


def tool_get_analytics(db: Session, user_id: UUID, product_id: str, days: int = 30) -> dict:
    pid = UUID(product_id)
    if not _owned_product(db, user_id, pid):
        return {"error": "product_not_found_or_forbidden"}
    return get_product_analytics(db, pid, days=days)


def tool_get_anomalies(db: Session, user_id: UUID, product_id: str, days: int = 60) -> dict:
    pid = UUID(product_id)
    if not _owned_product(db, user_id, pid):
        return {"error": "product_not_found_or_forbidden"}
    return detect_price_anomalies(db, pid, days=days)


def tool_get_matches(db: Session, user_id: UUID, product_id: str, min_score: float = 0.75) -> dict:
    pid = UUID(product_id)
    if not _owned_product(db, user_id, pid):
        return {"error": "product_not_found_or_forbidden"}
    return find_matches_for_product(db, user_id, pid, min_score=min_score)


def tool_get_insight(db: Session, user_id: UUID, product_id: str, days: int = 30) -> dict:
    pid = UUID(product_id)
    if not _owned_product(db, user_id, pid):
        return {"error": "product_not_found_or_forbidden"}
    return generate_insight(db, pid, days=days)


def tool_list_alerts(db: Session, user_id: UUID) -> dict:
    alerts = list_alerts(db, user_id, active_only=True)
    return {
        "alerts": [
            {
                "id": str(a.id),
                "product_id": str(a.product_id) if a.product_id else None,
                "rule_type": a.rule_type.value if hasattr(a.rule_type, "value") else str(a.rule_type),
                "threshold": a.threshold,
            }
            for a in alerts
        ],
        "count": len(alerts),
    }


TOOLS: dict[str, Callable] = {
    "list_products": tool_list_products,
    "get_analytics": tool_get_analytics,
    "get_anomalies": tool_get_anomalies,
    "get_matches": tool_get_matches,
    "get_insight": tool_get_insight,
    "list_alerts": tool_list_alerts,
}


def plan_tools(query: str) -> list[tuple[str, dict]]:
    """Naive intent router — deterministic, testable, no LLM required."""
    q = query.lower()
    calls: list[tuple[str, dict]] = []
    if any(w in q for w in ("alert", "notification", "notify")):
        calls.append(("list_alerts", {}))
    if any(w in q for w in ("anomal", "unusual", "spike", "drop", "weird")):
        calls.append(("list_products", {"limit": 10}))
        # analytics/anomalies need product ids — filled after list in run_analyst
        calls.append(("__per_product_anomalies__", {}))
    elif any(w in q for w in ("match", "duplicate", "same product", "equivalent")):
        calls.append(("list_products", {"limit": 10}))
        calls.append(("__per_product_matches__", {}))
    elif any(w in q for w in ("history", "trend", "analytics", "average", "volatility", "price")):
        calls.append(("list_products", {"limit": 10}))
        calls.append(("__per_product_analytics__", {}))
    elif any(w in q for w in ("summar", "insight", "recommend", "market")):
        calls.append(("list_products", {"limit": 5}))
        calls.append(("__per_product_insight__", {}))
    else:
        calls.append(("list_products", {"limit": 15}))
    return calls


def run_analyst(db: Session, user_id: UUID, query: str) -> dict[str, Any]:
    plan = plan_tools(query)
    tool_trace: list[dict] = []
    evidence: dict[str, Any] = {}
    product_ids: list[str] = []

    for name, kwargs in plan:
        if name == "list_products":
            result = tool_list_products(db, user_id, **kwargs)
            tool_trace.append({"tool": name, "args": kwargs, "ok": True})
            evidence["products"] = result
            product_ids = [p["id"] for p in result.get("products", [])]
            continue
        if name == "list_alerts":
            result = tool_list_alerts(db, user_id)
            tool_trace.append({"tool": name, "args": {}, "ok": True})
            evidence["alerts"] = result
            continue
        if name.startswith("__per_product_"):
            kind = name.replace("__per_product_", "").replace("__", "")
            bucket = []
            for pid in product_ids[:8]:
                if kind == "anomalies":
                    bucket.append(tool_get_anomalies(db, user_id, pid))
                elif kind == "matches":
                    bucket.append(tool_get_matches(db, user_id, pid))
                elif kind == "analytics":
                    bucket.append(tool_get_analytics(db, user_id, pid))
                elif kind == "insight":
                    bucket.append(tool_get_insight(db, user_id, pid))
            tool_trace.append({"tool": name, "args": {"product_ids": product_ids[:8]}, "ok": True})
            evidence[kind] = bucket
            continue
        fn = TOOLS.get(name)
        if not fn:
            tool_trace.append({"tool": name, "ok": False, "error": "unknown_tool"})
            continue
        result = fn(db, user_id, **kwargs)
        tool_trace.append({"tool": name, "args": kwargs, "ok": "error" not in result})
        evidence[name] = result

    answer = _compose_answer(query, evidence)
    return {
        "query": query,
        "answer": answer,
        "evidence": evidence,
        "tool_trace": tool_trace,
        "model": "deterministic_planner_v1",
        "llm_provider": getattr(settings, "llm_provider", None) or None,
        "limitations": [
            "Answers are grounded only in tools executed above.",
            "No unrestricted database access.",
            "Causal claims about competitor strategy are not invented.",
        ],
    }


def _compose_answer(query: str, evidence: dict) -> str:
    parts = []
    products = (evidence.get("products") or {}).get("products") or []
    if products:
        parts.append(f"You are tracking {len(products)} product(s) in scope for this question.")
        names = ", ".join(p["name"] for p in products[:5])
        parts.append(f"Sample: {names}.")
    analytics_list = evidence.get("analytics") or []
    if analytics_list:
        moved = []
        for a in analytics_list:
            if isinstance(a, dict) and a.get("percent_change") is not None:
                moved.append(f"{a.get('product_id', '?')}: {a['percent_change']}%")
        if moved:
            parts.append("Recent percent changes (from stored observations): " + "; ".join(moved[:5]) + ".")
    anomalies = evidence.get("anomalies") or []
    if anomalies:
        total = sum(int(a.get("anomaly_count") or 0) for a in anomalies if isinstance(a, dict))
        parts.append(f"Anomaly detectors flagged {total} point(s) across scanned products (statistical only).")
    alerts = evidence.get("alerts") or {}
    if alerts.get("count"):
        parts.append(f"You have {alerts['count']} active alert rule(s).")
    if not parts:
        parts.append("No matching catalog data was found for this query. Add products and scrape permitted sources first.")
    parts.append("All figures come from PriceLoop tool results, not free-form model memory.")
    return " ".join(parts)
