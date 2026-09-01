"""
Common interface every site adapter must implement.

Downstream code (dedup, storage, LLM insight layer) only ever talks to the
ProductData / RawPage types below -- never to raw HTML. This keeps the
pipeline site-agnostic: adding a new site means writing a new adapter and
registering it, not touching orchestration or scheduling.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawPage:
    url: str
    html: str
    status_code: int
    fetched_at: str


@dataclass
class ProductData:
    source: str
    url: str
    title: str
    price: Optional[float]
    currency: Optional[str]
    availability: Optional[str]
    rating: Optional[float] = None
    review_count: Optional[int] = None
    seller: Optional[str] = None
    raw_attributes: dict = field(default_factory=dict)
    scraped_at: str = ""


class BaseScraper:
    """Subclass this per site. Keep fetch (network) separate from parse (HTML)."""

    source_name: str = "base"

    def fetch(self, url: str) -> RawPage:
        """Fetch the page. Handles proxy selection, retries, and rate limiting
        for this specific source (see core/request_manager.py, rate_limiter.py)."""
        raise NotImplementedError

    def parse(self, raw_page: RawPage) -> ProductData:
        """Parse the fetched HTML into a ProductData record."""
        raise NotImplementedError

    def extract_product(self, url: str) -> ProductData:
        raw_page = self.fetch(url)
        return self.parse(raw_page)
