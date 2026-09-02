"""
Registry pattern: adding a new site is (1) write the adapter, (2) register it
here, (3) add fixtures under scraper/tests/fixtures/<source>/. No changes
needed to scheduling/orchestration.
"""

from typing import Dict, Type

from scraper.adapters.books_toscrape import BooksToScrapeAdapter
from scraper.core.base_scraper import BaseScraper

SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "books_toscrape": BooksToScrapeAdapter,
    # "amazon": AmazonScraper,
    # "walmart": WalmartScraper,
}


def get_scraper(source_name: str) -> BaseScraper:
    if source_name not in SCRAPERS:
        raise ValueError(f"No scraper registered for source: {source_name}")
    return SCRAPERS[source_name]()
