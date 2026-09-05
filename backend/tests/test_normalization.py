"""Unit tests for price / availability normalization."""

from decimal import Decimal

from app.services.normalization import (
    normalize_availability,
    normalize_price,
    normalize_title,
)


def test_normalize_price_rupee_symbol():
    price, currency = normalize_price("₹59,999")
    assert price == Decimal("59999")
    assert currency == "INR"


def test_normalize_price_with_code():
    price, currency = normalize_price("INR 59999.00")
    assert price == Decimal("59999.00")
    assert currency == "INR"


def test_normalize_price_plain_number():
    price, currency = normalize_price("1234.50")
    assert price == Decimal("1234.50")


def test_normalize_price_comma_as_decimal():
    price, currency = normalize_price("12,50 €")
    assert price == Decimal("12.50")
    assert currency == "EUR"


def test_normalize_price_european_thousands_and_comma_decimal():
    price, currency = normalize_price("1.299,50 €")
    assert price == Decimal("1299.50")
    assert currency == "EUR"


def test_normalize_price_us_thousands():
    price, currency = normalize_price("$1,299.99")
    assert price == Decimal("1299.99")
    assert currency == "USD"


def test_normalize_availability_in_stock():
    assert normalize_availability("In Stock") == "IN_STOCK"
    assert normalize_availability("available") == "IN_STOCK"


def test_normalize_availability_out_of_stock():
    assert normalize_availability("Out of Stock") == "OUT_OF_STOCK"
    assert normalize_availability("sold out") == "OUT_OF_STOCK"


def test_normalize_title_collapses_whitespace():
    assert normalize_title("  Sony   WH-1000XM5  ") == "Sony WH-1000XM5"
