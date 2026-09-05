"""
Canonical data normalization helpers.
Different sites return prices/availability in many formats.
This module converts them into a clean internal representation.
"""

from decimal import Decimal, InvalidOperation
import re
from typing import Any


CURRENCY_SYMBOLS = {
    "₹": "INR",
    "rs": "INR",
    "rs.": "INR",
    "inr": "INR",
    "$": "USD",
    "usd": "USD",
    "€": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "gbp": "GBP",
}


def normalize_price(raw: Any) -> tuple[Decimal | None, str]:
    """
    Convert messy price strings into (Decimal, currency).
    Examples handled:
      ₹59,999  |  59999 INR  |  ₹59,999.00  |  INR 59999  |  59,999
    """
    if raw is None:
        return None, "INR"

    if isinstance(raw, (int, float, Decimal)):
        return Decimal(str(raw)), "INR"

    text = str(raw).strip().lower()
    currency = "INR"

    # Detect currency symbol / code
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in text:
            currency = code
            text = text.replace(symbol, " ")
            break

    # Keep only digits, dots and commas
    cleaned = re.sub(r"[^\d.,]", "", text)
    if not cleaned:
        return None, currency

    # "," is ambiguous: "1,299.00" uses it as a thousands separator, but
    # "12,50" (common outside the US/UK) uses it as the decimal point.
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            # comma comes after dot -> comma is decimal separator (e.g. 1.299,50)
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # dot comes after comma -> comma is thousands separator (e.g. 1,299.50)
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        after_last_comma = cleaned.split(",")[-1]
        if len(after_last_comma) == 2:
            # "12,50" style -> comma is decimal separator
            cleaned = cleaned.replace(",", ".")
        else:
            # "1,299" style -> comma is thousands separator
            cleaned = cleaned.replace(",", "")

    try:
        return Decimal(cleaned), currency
    except (InvalidOperation, ValueError):
        return None, currency


def normalize_availability(raw: Any) -> str:
    """Map free-text availability to canonical enum values."""
    if raw is None:
        return "UNKNOWN"

    text = str(raw).strip().lower()

    if any(x in text for x in ["in stock", "available", "in_stock", "instock"]):
        return "IN_STOCK"
    if any(x in text for x in ["out of stock", "unavailable", "sold out", "out_of_stock"]):
        return "OUT_OF_STOCK"
    if "preorder" in text or "pre-order" in text:
        return "PREORDER"
    return "UNKNOWN"


def normalize_title(raw: Any) -> str | None:
    if not raw:
        return None
    title = re.sub(r"\s+", " ", str(raw).strip())
    return title[:500] if title else None
