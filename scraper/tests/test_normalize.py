"""
Regression tests for price/availability normalization -- in particular the
comma-as-decimal-vs-thousands-separator ambiguity, which previously parsed
European-style prices like "12,50" as 1250 (~100x too high).
"""

from decimal import Decimal

from scraper.parsers.normalize import normalize_availability, normalize_price


def test_us_style_decimal_point():
    assert normalize_price("$19.99") == (Decimal("19.99"), "USD")


def test_thousands_comma_with_decimal_point():
    assert normalize_price("$1,234.56") == (Decimal("1234.56"), "USD")


def test_european_comma_as_decimal_separator():
    assert normalize_price("€12,50") == (Decimal("12.50"), "EUR")


def test_european_full_format_both_separators():
    # thousands separator is "." here, decimal separator is ","
    assert normalize_price("€1.234,56") == (Decimal("1234.56"), "EUR")


def test_comma_as_thousands_separator_no_decimal():
    assert normalize_price("$1,234") == (Decimal("1234"), "USD")


def test_iso_code_without_symbol():
    assert normalize_price("59999 INR") == (Decimal("59999"), "INR")


def test_empty_and_none_are_unparseable():
    assert normalize_price("") == (None, None)
    assert normalize_price(None) == (None, None)
    assert normalize_price("Free") == (None, None)


def test_availability_in_stock_with_quantity():
    assert normalize_availability("In stock (22 available)") == ("IN_STOCK", 22)


def test_availability_out_of_stock():
    assert normalize_availability("Out of Stock") == ("OUT_OF_STOCK", None)


def test_availability_unrecognized_defaults_to_unknown():
    assert normalize_availability("Ships in 3 days") == ("UNKNOWN", None)
