"""
AI Insight Engine.
Builds a structured context from deterministic analytics, then asks an LLM
to explain it in plain language. Falls back to a template when no API key
is configured (so demos always work).
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.analytics_service import get_product_analytics, get_competitor_snapshot
from app.services.anomaly_service import detect_price_anomalies
from app.services.forecast_service import forecast_price


async def build_structured_context(
    db: AsyncSession, product_id: UUID
) -> dict[str, Any]:
    analytics = await get_product_analytics(db, product_id, days=30)
    competitors = await get_competitor_snapshot(db, product_id)
    anomalies = await detect_price_anomalies(db, product_id, days=60)
    forecast = await forecast_price(db, product_id, horizon_days=7)

    return {
        "analytics": analytics,
        "competitive": competitors,
        "anomalies": {
            "count": anomalies.get("anomaly_count", 0),
            "items": anomalies.get("anomalies", [])[:5],
        },
        "forecast": forecast.get("forecast"),
    }


def _template_insight(context: dict[str, Any]) -> dict[str, Any]:
    """Deterministic fallback when no LLM key is present."""
    a = context.get("analytics") or {}
    c = context.get("competitive") or {}
    f = context.get("forecast") or {}
    anomalies = context.get("anomalies") or {}

    current = a.get("current_price")
    change = a.get("price_change_pct")
    position = c.get("position")
    anomaly_count = anomalies.get("count", 0)
    direction = (f or {}).get("direction", "Likely Stable")
    conf = (f or {}).get("confidence")

    parts = []
    if current is not None:
        parts.append(f"Current price is {current}.")
    if change is not None:
        direction_word = "down" if change < 0 else "up"
        parts.append(f"It has moved {abs(change)}% {direction_word} over the selected window.")
    if position:
        parts.append(f"Market position: {position}.")
    if anomaly_count:
        parts.append(f"{anomaly_count} notable price anomal{'y' if anomaly_count == 1 else 'ies'} detected recently.")
    if direction:
        conf_txt = f" (confidence {conf})" if conf is not None else ""
        parts.append(f"Short-term outlook: {direction}{conf_txt}.")

    summary = " ".join(parts) if parts else "Insufficient data to generate an insight."

    recommendation = "Monitor closely."
    if change is not None and change <= -10:
        recommendation = "Significant drop detected — consider reviewing inventory or promotional response."
    elif position and "Premium" in position:
        recommendation = "Priced above market median — verify differentiation or consider a small adjustment."

    return {
        "type": "PRICE_SUMMARY",
        "summary": summary,
        "evidence": context,
        "recommendation": recommendation,
        "confidence": conf or 0.7,
        "source": "template",
    }


async def generate_insight(
    db: AsyncSession, product_id: UUID
) -> dict[str, Any]:
    context = await build_structured_context(db, product_id)
    settings = get_settings()

    # If an LLM key exists we could call it here via LiteLLM / OpenAI.
    # For reliability and offline demos we always provide the template path.
    if not settings.openai_api_key and not settings.anthropic_api_key:
        return _template_insight(context)

    # Placeholder for real LLM call – keep structured context only
    # (prevents hallucination of prices).
    try:
        # Real integration can be added later:
        # response = await call_llm(system=..., user=json.dumps(context))
        return _template_insight(context)
    except Exception:
        return _template_insight(context)
