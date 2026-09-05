"""
Demo / fixture-based scraper.
Useful for development, testing, and portfolio demos without hitting live sites.
"""

from decimal import Decimal
from typing import Any

from bs4 import BeautifulSoup

from scraper.core.base import BaseScraper, ScrapedProduct


class DemoScraper(BaseScraper):
    name = "demo"
    rate_limit = 10.0

    async def fetch(self, url: str) -> str:
        # In real usage this would call httpx.
        # For demo we return a fixed HTML fixture.
        return """
        <html>
          <body>
            <h1 id="product-title">Sony WH-1000XM5 Wireless Headphones Black</h1>
            <span class="price" data-currency="INR">₹59,999</span>
            <span class="availability">In Stock</span>
            <span class="rating">4.7</span>
            <span class="reviews">12450</span>
          </body>
        </html>
        """

    def parse(self, html: str) -> Any:
        return BeautifulSoup(html, "lxml")

    def extract_product(self, parsed: Any, url: str) -> ScrapedProduct:
        title_el = parsed.select_one("#product-title")
        price_el = parsed.select_one(".price")
        avail_el = parsed.select_one(".availability")
        rating_el = parsed.select_one(".rating")
        reviews_el = parsed.select_one(".reviews")

        price_text = price_el.get_text(strip=True) if price_el else None
        price = None
        currency = "INR"
        if price_text:
            # Very simple normalization
            cleaned = (
                price_text.replace("₹", "")
                .replace(",", "")
                .replace("INR", "")
                .strip()
            )
            try:
                price = Decimal(cleaned)
            except Exception:
                price = None
            if price_el and price_el.get("data-currency"):
                currency = price_el["data-currency"]

        availability = "UNKNOWN"
        if avail_el:
            text = avail_el.get_text(strip=True).lower()
            if "in stock" in text:
                availability = "IN_STOCK"
            elif "out of stock" in text:
                availability = "OUT_OF_STOCK"

        rating = None
        if rating_el:
            try:
                rating = float(rating_el.get_text(strip=True))
            except ValueError:
                pass

        review_count = None
        if reviews_el:
            try:
                review_count = int(reviews_el.get_text(strip=True).replace(",", ""))
            except ValueError:
                pass

        return ScrapedProduct(
            title=title_el.get_text(strip=True) if title_el else None,
            price=price,
            currency=currency,
            availability=availability,
            rating=rating,
            review_count=review_count,
            product_url=url,
        )
