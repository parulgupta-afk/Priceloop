"""
Natural-language query layer.
Maps common English questions to existing deterministic services.
No free-form SQL generation – keeps the system safe and auditable.
"""

import re
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import get_product_analytics, get_competitor_snapshot
from app.services.anomaly_service import detect_price_anomalies
from app.services.forecast_service import forecast_price
from app.services.insight_service import generate_insight


async def answer_question(
    db: AsyncSession,
    product_id: UUID | None,
    question: str,
) -> dict[str, Any]:
    q = question.lower().strip()

    # Intent detection (simple keyword rules – upgrade later with a classifier)
    if any(w in q for w in ["forecast", "predict", "next week", "will the price"]):
        if not product_id:
            return {"intent": "forecast", "error": "product_id required"}
        data = await forecast_price(db, product_id)
        return {
            "intent": "forecast",
            "question": question,
            "answer": data,
            "explanation": "Mapped to the forecasting engine.",
        }

    if any(w in q for w in ["anomal", "unusual", "spike", "drop suddenly"]):
        if not product_id:
            return {"intent": "anomaly", "error": "product_id required"}
        data = await detect_price_anomalies(db, product_id)
        return {
            "intent": "anomaly",
            "question": question,
            "answer": data,
            "explanation": "Mapped to the anomaly detector.",
        }

    if any(w in q for w in ["competitor", "cheapest", "market", "position"]):
        if not product_id:
            return {"intent": "competitive", "error": "product_id required"}
        data = await get_competitor_snapshot(db, product_id)
        return {
            "intent": "competitive",
            "question": question,
            "answer": data,
            "explanation": "Mapped to competitive analytics.",
        }

    if any(w in q for w in ["why", "explain", "insight", "summary", "what happened"]):
        if not product_id:
            return {"intent": "insight", "error": "product_id required"}
        data = await generate_insight(db, product_id)
        return {
            "intent": "insight",
            "question": question,
            "answer": data,
            "explanation": "Mapped to the AI insight engine (structured context).",
        }

    # Default → general analytics
    if product_id:
        data = await get_product_analytics(db, product_id)
        return {
            "intent": "analytics",
            "question": question,
            "answer": data,
            "explanation": "Defaulted to price analytics.",
        }

    return {
        "intent": "unknown",
        "question": question,
        "answer": None,
        "explanation": "Could not map the question. Try asking about price, forecast, anomalies, or competitors for a specific product.",
    }
