"""
Celery tasks for background scraping.
In this phase we keep a simple synchronous-style task that will later
be expanded with proper async DB sessions and batching.
"""

import asyncio
from uuid import UUID

from app.workers.celery_app import celery_app


@celery_app.task(name="scrape.listing", bind=True, max_retries=3)
def scrape_listing_task(self, listing_id: str) -> dict:
    """
    Background task that scrapes a single listing.
    For now it runs the async scrape_service inside an event loop.
    """
    from app.core.database import AsyncSessionLocal
    from app.services.scrape_service import scrape_listing

    async def _run():
        async with AsyncSessionLocal() as session:
            try:
                observation = await scrape_listing(session, UUID(listing_id))
                await session.commit()
                return {
                    "status": "success",
                    "listing_id": listing_id,
                    "observation_id": str(observation.id),
                    "price": str(observation.price),
                    "currency": observation.currency,
                }
            except Exception as exc:
                await session.rollback()
                raise self.retry(exc=exc, countdown=30)

    return asyncio.run(_run())


@celery_app.task(name="scrape.all_active")
def scrape_all_active_listings() -> dict:
    """
    Find every active listing and enqueue individual scrape tasks.
    This keeps the system scalable – each listing is its own job.
    """
    import asyncio
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.product import ProductListing

    async def _collect():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProductListing.id).where(ProductListing.is_active == True)
            )
            return [str(row[0]) for row in result.all()]

    listing_ids = asyncio.run(_collect())
    for lid in listing_ids:
        scrape_listing_task.delay(lid)

    return {
        "status": "enqueued",
        "count": len(listing_ids),
        "listing_ids": listing_ids,
    }
