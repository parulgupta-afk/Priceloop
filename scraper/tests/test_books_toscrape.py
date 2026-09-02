"""
Fixture-based test: parses a saved HTML snapshot rather than hitting the
live site. This is what catches "site changed its layout, parser now
returns null" in CI before it reaches production -- see Phase 19/20
(scraper observability + self-healing) for what happens when this fails
against a live scrape instead.
"""

from pathlib import Path

from scraper.adapters.books_toscrape import BooksToScrapeAdapter
from scraper.core.base_scraper import RawPage

FIXTURE = Path(__file__).parent / "fixtures" / "books_toscrape" / "product_page.html"


def test_parses_title_price_and_availability():
    html = FIXTURE.read_text()
    raw_page = RawPage(
        url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        html=html,
        status_code=200,
        fetched_at="2026-09-01T00:00:00+00:00",
    )

    adapter = BooksToScrapeAdapter()
    product = adapter.parse(raw_page)

    assert product.title == "A Light in the Attic"
    assert product.price == 51.77
    assert product.currency == "GBP"
    assert product.availability == "IN_STOCK"
    assert product.raw_attributes["quantity_available"] == 22
