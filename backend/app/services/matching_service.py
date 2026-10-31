"""
Hybrid product matching: deterministic hints + fuzzy title/brand/model + variant penalties.
"""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import Product

_STORAGE = re.compile(r"(\d+)\s*(gb|tb)", re.I)
_COLOR = re.compile(r"\b(black|white|blue|red|green|silver|gold|gray|grey|purple|pink)\b", re.I)


def _norm(text: str | None) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _storage_tokens(text: str) -> set[str]:
    return {f"{m.group(1)}{m.group(2).lower()}" for m in _STORAGE.finditer(text or "")}


def _color_tokens(text: str) -> set[str]:
    return {m.group(1).lower() for m in _COLOR.finditer(text or "")}


def compute_match_score(a: Product, b: Product) -> dict[str, Any]:
    name_a, name_b = _norm(a.name), _norm(b.name)
    brand_a = _norm(a.brand) or (name_a.split()[0] if name_a else "")
    brand_b = _norm(b.brand) or (name_b.split()[0] if name_b else "")
    model_a = _norm(getattr(a, "model", None) or "")
    model_b = _norm(getattr(b, "model", None) or "")

    title_sim = SequenceMatcher(None, name_a, name_b).ratio()
    brand_match = 1.0 if brand_a and brand_a == brand_b else (
        0.6 if brand_a and brand_b and (brand_a in brand_b or brand_b in brand_a) else 0.0
    )
    model_sim = SequenceMatcher(None, model_a, model_b).ratio() if model_a and model_b else 0.0

    # Exact-ish SKU/gtin if present
    sku_bonus = 0.0
    if getattr(a, "sku", None) and getattr(b, "sku", None) and _norm(a.sku) == _norm(b.sku):
        sku_bonus = 0.25
    if getattr(a, "gtin", None) and getattr(b, "gtin", None) and _norm(a.gtin) == _norm(b.gtin):
        sku_bonus = 0.35

    final = 0.30 * title_sim + 0.25 * brand_match + 0.25 * model_sim + sku_bonus

    # Variant penalties: different storage/color => not the same offer
    stor_a, stor_b = _storage_tokens(a.name or ""), _storage_tokens(b.name or "")
    col_a, col_b = _color_tokens(a.name or ""), _color_tokens(b.name or "")
    penalties = []
    if stor_a and stor_b and stor_a.isdisjoint(stor_b):
        final -= 0.25
        penalties.append("storage_mismatch")
    if col_a and col_b and col_a.isdisjoint(col_b):
        final -= 0.10
        penalties.append("color_mismatch")

    final = round(min(max(final, 0.0), 1.0), 3)
    if final >= 0.90:
        label = "likely_same"
    elif final >= 0.75:
        label = "possible_match"
    else:
        label = "unlikely"

    return {
        "score": final,
        "label": label,
        "matching_method": "hybrid_fuzzy_v2",
        "components": {
            "title_similarity": round(title_sim, 3),
            "brand_match": brand_match,
            "model_similarity": round(model_sim, 3),
            "sku_gtin_bonus": sku_bonus,
        },
        "penalties": penalties,
        "matched_attributes": [
            x for x, ok in [
                ("brand", brand_match >= 0.6),
                ("model", model_sim >= 0.7),
                ("title", title_sim >= 0.7),
                ("sku_or_gtin", sku_bonus > 0),
            ] if ok
        ],
        "review_required": final >= 0.75 and final < 0.90,
        "reason": f"title={title_sim:.2f} brand={brand_match:.2f} model={model_sim:.2f} penalties={penalties}",
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
        .filter(Product.user_id == user_id, Product.id != product_id)
        .limit(300)
        .all()
    )
    scored = []
    for other in candidates:
        s = compute_match_score(product, other)
        if s["score"] >= min_score:
            scored.append({"product_id": str(other.id), "name": other.name, "brand": other.brand, **s})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "product_id": str(product_id),
        "name": product.name,
        "match_count": len(scored[:limit]),
        "matches": scored[:limit],
        "min_score": min_score,
    }
