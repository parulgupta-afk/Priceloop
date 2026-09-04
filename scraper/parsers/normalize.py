"""
Site-specific scrapers return raw strings ("£51.77", "In stock (22 available)").
This module is the single place that turns those into the canonical shapes
every downstream consumer (DB, analytics, LLM layer) can rely on.

Keeping this separate from any one adapter means a new site only needs to
supply raw strings in whatever format it uses -- the normalization logic
(and its test coverage) is shared.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

CURRENCY_SYMBOLS = {
    "£": "GBP",
    "$": "USD",
    "€": "EUR",
    "₹": "INR",
}


def normalize_price(raw: str) -> Tuple[Optional[Decimal], Optional[str]]:
    """"£51.77" -> (Decimal("51.77"), "GBP"). Returns (None, None) if unparseable."""
    if not raw:
        return None, None

    raw = raw.strip()
    currency = None
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in raw:
            currency = code
            break

    # Explicit ISO code already present, e.g. "59999 INR"
    iso_match = re.search(r"\b([A-Z]{3})\b", raw)
    if iso_match and not currency:
        currency = iso_match.group(1)

    numeric = re.sub(r"[^\d.,]", "", raw)
    if not numeric:
        return None, currency

    # "," is ambiguous: "1,299.00" uses it as a thousands separator, but
    # "12,50" (common outside the US/UK) uses it as the decimal point.
    # Disambiguate instead of always stripping it -- previously this parsed
    # "12,50" as 1250 (roughly 100x too high).
    if "," in numeric and "." in numeric:
        if numeric.rfind(",") > numeric.rfind("."):
            # comma comes after the dot -> comma is the decimal separator
            numeric = numeric.replace(".", "").replace(",", ".")
        else:
            numeric = numeric.replace(",", "")
    elif "," in numeric:
        after_last_comma = numeric.split(",")[-1]
        if len(after_last_comma) == 2:
            # "12,50" style -> comma is a decimal separator
            numeric = numeric.replace(",", ".")
        else:
            # "1,299" style -> comma is a thousands separator
            numeric = numeric.replace(",", "")

    try:
        amount = Decimal(numeric)
    except InvalidOperation:
        return None, currency

    return amount, currency


AVAILABILITY_MAP = {
    "in stock": "IN_STOCK",
    "out of stock": "OUT_OF_STOCK",
    "available": "IN_STOCK",
    "unavailable": "OUT_OF_STOCK",
    "backorder": "BACKORDER",
    "pre-order": "PREORDER",
}


def normalize_availability(raw: str) -> Tuple[str, Optional[int]]:
    """"In stock (22 available)" -> ("IN_STOCK", 22). Defaults to "UNKNOWN" if unrecognized."""
    if not raw:
        return "UNKNOWN", None

    text = raw.strip().lower()

    quantity = None
    qty_match = re.search(r"(\d+)\s+available", text)
    if qty_match:
        quantity = int(qty_match.group(1))

    for phrase, status in AVAILABILITY_MAP.items():
        if phrase in text:
            return status, quantity

    return "UNKNOWN", quantity
