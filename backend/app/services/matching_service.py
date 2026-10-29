"""
Deterministic + fuzzy product matching across catalog (sync).
Explains scores; does not silently merge incompatible variants.
"""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import Product


def _norm(text: str | None) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def compute_match_score(a: Product, b: Product) -> dict[str, Any]:
    brand_a = _norm(a.brand) or (_norm(a.name).split()[0] if _norm(a.name) else "")
    brand_b = _norm(b.brand) or (_norm(b.name).split()[0] if _norm(b.name) else "")
    model_a = _norm(getattr(a, "model", None) or "")
    model_b = _norm(getattr(b, "model", None) or "")
    title_sim = SequenceMatcher(None, _norm(a.name), _norm(b.name)).ratio()
    brand_match = 1.0 if brand_a and brand_a == brand_b else (
        0.6 if brand_a and brand_b and (brand_a in brand_b or brand_b in brand_a) else 0.0
    )
    model_sim = SequenceMatcher(None, model_a, model_b).ratio() if model_a and model_b else 0.0
    final = round(min(max(0.35 * title_sim + 0.30 * brand_match + 0.35 * model_sim, 0.0), 1.0), 3)
    if final >= 0.90:
        label = "likely_same"
    elif final >= 0.75:
        label = "possible_match"
    else:
        label = "unlikely"
    return {
        "score": final,
        "label": label,
        "components": {
            "title_similarity": round(title_sim, 3),
            "brand_match": brand_match,
            "model_similarity": round(model_sim, 3),
        },
        "reason": f"title={title_sim:.2f}, brand={brand_match:.2f}, model={model_sim:.2f}",
    }


def find_matches_for_product(
    db: Session,
    user_id: UUID,
    product_id: UUID,
    min_score: float = 0.75,
    limit: int = 20,
) -> dict[str, Any]:
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        return {"product_id": str(product_id), "matches": [], "error": "not_found"}
    candidates = (
        db.query(Product)
        .filter(Product.user_id == user_id, Product.id != product_id, Product.is_active.is_(True))
        .limit(200)
        .all()
    )
    scored = []
    for other in candidates:
        s = compute_match_score(product, other)
        if s["score"] >= min_score:
            scored.append({
                "product_id": str(other.id),
                "name": other.name,
                "brand": other.brand,
                **s,
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "product_id": str(product_id),
        "name": product.name,
        "match_count": len(scored[:limit]),
        "matches": scored[:limit],
        "min_score": min_score,
    }
