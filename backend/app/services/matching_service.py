"""
Product matching foundation.
Uses rule-based + fuzzy string similarity.
Later we will add sentence-transformers embeddings + pgvector.
"""

import re
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.matching import ProductMatch
from app.models.product import Product


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _extract_brand_model(name: str, brand: str | None, model: str | None) -> tuple[str, str]:
    brand_n = _normalize_text(brand) if brand else ""
    model_n = _normalize_text(model) if model else ""
    name_n = _normalize_text(name)

    # Very simple heuristics – will be improved
    if not brand_n and name_n:
        parts = name_n.split()
        if parts:
            brand_n = parts[0]
    return brand_n, model_n or name_n


def compute_match_score(a: Product, b: Product) -> dict[str, Any]:
    """
    Return a structured score between two products.
    """
    brand_a, model_a = _extract_brand_model(a.name, a.brand, a.model)
    brand_b, model_b = _extract_brand_model(b.name, b.brand, b.model)

    title_sim = SequenceMatcher(None, _normalize_text(a.name), _normalize_text(b.name)).ratio()
    brand_match = 1.0 if brand_a and brand_a == brand_b else (0.6 if brand_a in brand_b or brand_b in brand_a else 0.0)
    model_sim = SequenceMatcher(None, model_a, model_b).ratio() if model_a and model_b else 0.0

    # Weighted final score
    final = (
        0.35 * title_sim
        + 0.30 * brand_match
        + 0.35 * model_sim
    )
    final = round(min(max(final, 0.0), 1.0), 3)

    if final >= 0.90:
        level = "HIGH"
    elif final >= 0.75:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "confidence": final,
        "level": level,
        "breakdown": {
            "title_similarity": round(title_sim, 3),
            "brand_match": brand_match,
            "model_similarity": round(model_sim, 3),
        },
        "method": "fuzzy+rules",
    }


async def find_potential_matches(
    db: AsyncSession,
    product_id: UUID,
    min_confidence: float = 0.60,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Compare the given product against other products of the same user
    and return ranked potential matches.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    target = result.scalar_one_or_none()
    if not target:
        return []

    others = await db.execute(
        select(Product).where(
            Product.user_id == target.user_id,
            Product.id != product_id,
            Product.is_active == True,
        )
    )
    candidates = list(others.scalars().all())

    scored = []
    for cand in candidates:
        score = compute_match_score(target, cand)
        if score["confidence"] >= min_confidence:
            scored.append(
                {
                    "product_id": str(cand.id),
                    "name": cand.name,
                    "brand": cand.brand,
                    "model": cand.model,
                    **score,
                }
            )

    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:limit]


async def create_match(
    db: AsyncSession,
    product_a_id: UUID,
    product_b_id: UUID,
    confidence: float,
    method: str = "fuzzy+rules",
    reviewed: bool = False,
    is_confirmed: bool = False,
) -> ProductMatch:
    # Avoid duplicates / direction issues
    a, b = sorted([product_a_id, product_b_id], key=str)
    existing = await db.execute(
        select(ProductMatch).where(
            ProductMatch.product_a_id == a,
            ProductMatch.product_b_id == b,
        )
    )
    match = existing.scalar_one_or_none()
    if match:
        match.confidence = confidence
        match.method = method
        match.reviewed = reviewed
        match.is_confirmed = is_confirmed
    else:
        match = ProductMatch(
            product_a_id=a,
            product_b_id=b,
            confidence=confidence,
            method=method,
            reviewed=reviewed,
            is_confirmed=is_confirmed,
        )
        db.add(match)
    await db.flush()
    await db.refresh(match)
    return match
