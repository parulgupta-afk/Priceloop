"""
Adapter for books.toscrape.com -- a site explicitly built and hosted for
scraping practice, used here as the "one permitted/public source" to prove
out the fetch -> parse -> ProductData pipeline before pointing adapters at
any real e-commerce site with its own terms to respect.

Fetch and parse are kept separate: fetch() does network I/O and can be
retried/mocked independently of parse(), which is pure and unit-testable
against saved HTML fixtures (see scraper/tests/fixtures/books_toscrape/).
"""

from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from scraper.core.base_scraper import BaseScraper, ProductData, RawPage
from scraper.parsers.normalize import normalize_availability, normalize_price


class BooksToScrapeAdapter(BaseScraper):
    source_name = "books_toscrape"

    def fetch(self, url: str) -> RawPage:
        response = httpx.get(url, timeout=10.0, headers={"User-Agent": "priceloop-scraper/0.1"})
        response.raise_for_status()
        return RawPage(
            url=url,
            html=response.text,
            status_code=response.status_code,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )

    def parse(self, raw_page: RawPage) -> ProductData:
        soup = BeautifulSoup(raw_page.html, "html.parser")

        title_el = soup.select_one(".product_main h1")
        price_el = soup.select_one(".product_main .price_color")
        availability_el = soup.select_one(".product_main .availability")

        title = title_el.get_text(strip=True) if title_el else ""
        price, currency = normalize_price(price_el.get_text(strip=True) if price_el else "")
        availability, quantity = normalize_availability(
            availability_el.get_text(strip=True) if availability_el else ""
        )

        return ProductData(
            source=self.source_name,
            url=raw_page.url,
            title=title,
            price=float(price) if price is not None else None,
            currency=currency,
            availability=availability,
            raw_attributes={"quantity_available": quantity},
            scraped_at=raw_page.fetched_at,
        )
