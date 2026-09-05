from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


@dataclass
class ScrapedProduct:
    title: str | None
    price: Decimal | None
    currency: str
    availability: str  # IN_STOCK | OUT_OF_STOCK | UNKNOWN | PREORDER
    rating: float | None = None
    review_count: int | None = None
    seller: str | None = None
    product_url: str | None = None
    image_url: str | None = None
    raw: dict[str, Any] | None = None
    scraped_at: datetime = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now(timezone.utc)


class BaseScraper(ABC):
    """
    Common interface for all site adapters.
    Every adapter must implement fetch → parse → extract.
    """

    name: str = "base"
    rate_limit: float = 1.0  # requests per second

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Fetch raw HTML (or JSON) for the given URL."""
        ...

    @abstractmethod
    def parse(self, html: str) -> Any:
        """Parse HTML into a structure suitable for extraction."""
        ...

    @abstractmethod
    def extract_product(self, parsed: Any, url: str) -> ScrapedProduct:
        """Extract canonical product fields from parsed content."""
        ...

    async def scrape(self, url: str) -> ScrapedProduct:
        """Full pipeline: fetch → parse → extract."""
        html = await self.fetch(url)
        parsed = self.parse(html)
        return self.extract_product(parsed, url)
