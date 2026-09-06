"""
Orchestrates scraping a ProductListing and storing a PriceObservation.
Uses the scraper package adapters. Uses the same sync Session as the rest of the app.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import AvailabilityStatus, PriceObservation, ProductListing, Source
from app.services.normalization import normalize_availability, normalize_price, normalize_title

_here = Path(__file__).resolve()
for candidate in (
    _here.parents[3],
    _here.parents[2],
    Path("/app"),
    Path("/app/..").resolve(),
):
    if (candidate / "scraper").is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from scraper.adapters.demo import DemoScraper  # noqa: E402
    from scraper.core.base import BaseScraper  # noqa: E402
except ModuleNotFoundError:

    class BaseScraper:  # type: ignore
        def scrape(self, url: str):
            return {
                "title": "Unavailable",
                "price": None,
                "currency": "USD",
                "availability": "UNKNOWN",
            }

    class DemoScraper(BaseScraper):  # type: ignore
        def scrape(self, url: str):
            return {
                "title": "Demo listing",
                "price": 99.0,
                "currency": "USD",
                "availability": "IN_STOCK",
            }


ADAPTER_REGISTRY: dict[str, type] = {
    "demo": DemoScraper,
}


def get_adapter(source_name: str):
    key = (source_name or "demo").lower().strip()
    cls = ADAPTER_REGISTRY.get(key, DemoScraper)
    return cls()


def scrape_listing(db: Session, listing_id: UUID) -> PriceObservation:
    """Fetch listing, run adapter, normalize, persist observation (sync)."""
    listing = (
        db.query(ProductListing)
        .filter(ProductListing.id == listing_id)
        .first()
    )
    if listing is None:
        raise ValueError(f"Listing {listing_id} not found")

    source_name = "demo"
    if listing.source_id:
        source = db.query(Source).filter(Source.id == listing.source_id).first()
        if source:
            source_name = source.name

    adapter = get_adapter(source_name)
    raw = adapter.scrape(listing.external_url) or {}

    title = normalize_title(raw.get("title") or listing.title or "")
    price_val, detected_currency = normalize_price(raw.get("price"))
    currency = (raw.get("currency") or detected_currency or listing.currency or "USD")[:3].upper()
    availability = normalize_availability(raw.get("availability")) or AvailabilityStatus.UNKNOWN.value

    if price_val is None:
        raise ValueError(f"No price returned for listing {listing_id}")

    obs = PriceObservation(
        listing_id=listing.id,
        price=Decimal(str(price_val)),
        currency=currency,
        availability=str(availability),
        scraped_at=datetime.now(timezone.utc).replace(tzinfo=None),
        raw_data=raw if isinstance(raw, dict) else {"raw": str(raw)},
    )
    db.add(obs)

    listing.current_price = obs.price
    listing.currency = currency
    listing.availability = obs.availability
    listing.last_scraped_at = obs.scraped_at
    if title:
        listing.title = title

    db.flush()
    return obs
