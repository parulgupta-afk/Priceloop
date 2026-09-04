"""
Price history metrics and competitive positioning.
All calculations are deterministic and based only on stored observations.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from statistics import mean, median
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import PriceObservation, Product, ProductListing


def _safe_float(value: Decimal | float | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _pct_change(old: float | None, new: float | None) -> float | None:
    if old is None or new is None or old == 0:
        return None
    return round(((new - old) / old) * 100, 2)


async def get_product_analytics(
    db: AsyncSession,
    product_id: UUID,
    days: int = 30,
) -> dict[str, Any]:
    """
    Compute core price intelligence metrics for a product.
    """
    # Ownership is checked by the caller
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(PriceObservation)
        .join(ProductListing)
        .where(
            ProductListing.product_id == product_id,
            PriceObservation.scraped_at >= cutoff,
        )
        .order_by(PriceObservation.scraped_at.asc())
    )
    observations = list(result.scalars().all())

    if not observations:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": 0,
            "message": "No price observations in the selected window",
        }

    prices = [float(o.price) for o in observations if o.price is not None]
    if not prices:
        return {
            "product_id": str(product_id),
            "window_days": days,
            "observation_count": len(observations),
            "message": "Observations exist but no valid prices",
        }

    current = prices[-1]
    previous = prices[-2] if len(prices) > 1 else None
    min_p = min(prices)
    max_p = max(prices)
    avg_p = mean(prices)
    med_p = median(prices)

    # Simple volatility: std-dev / mean (coefficient of variation)
    if len(prices) > 1 and avg_p > 0:
        variance = sum((p - avg_p) ** 2 for p in prices) / (len(prices) - 1)
        std = variance ** 0.5
        volatility = round(std / avg_p, 4)
    else:
        volatility = 0.0

    # 7-day and 30-day change (using earliest observation in window as baseline)
    change_pct = _pct_change(prices[0], current)
    day_change_pct = _pct_change(previous, current)

    return {
        "product_id": str(product_id),
        "window_days": days,
        "observation_count": len(observations),
        "current_price": current,
        "previous_price": previous,
        "min_price": min_p,
        "max_price": max_p,
        "avg_price": round(avg_p, 2),
        "median_price": round(med_p, 2),
        "price_change_pct": change_pct,          # from start of window
        "last_change_pct": day_change_pct,       # last observation vs previous
        "volatility": volatility,
        "currency": observations[-1].currency if observations else "INR",
        "first_scraped_at": observations[0].scraped_at.isoformat(),
        "last_scraped_at": observations[-1].scraped_at.isoformat(),
    }


async def get_competitor_snapshot(
    db: AsyncSession,
    product_id: UUID,
) -> dict[str, Any]:
    """
    Simple competitive view: current prices of all listings of this product.
    Later this will expand to cross-product matching.
    """
    result = await db.execute(
        select(ProductListing)
        .where(ProductListing.product_id == product_id, ProductListing.is_active == True)
    )
    listings = list(result.scalars().all())

    competitors = []
    prices = []
    for listing in listings:
        if listing.current_price is not None:
            prices.append(float(listing.current_price))
            competitors.append(
                {
                    "listing_id": str(listing.id),
                    "source_id": str(listing.source_id),
                    "title": listing.title,
                    "price": float(listing.current_price),
                    "currency": listing.currency,
                    "availability": listing.availability.value if listing.availability else None,
                    "last_scraped_at": listing.last_scraped_at.isoformat()
                    if listing.last_scraped_at
                    else None,
                    "url": listing.external_url,
                }
            )

    market_median = median(prices) if prices else None
    market_avg = mean(prices) if prices else None
    lowest = min(prices) if prices else None
    highest = max(prices) if prices else None

    # Rough position label
    position = None
    if market_median is not None and prices:
        # Use the first listing as "your" price for now
        your_price = prices[0]
        if your_price <= market_median * 0.97:
            position = "Competitive / Below market"
        elif your_price >= market_median * 1.05:
            position = "Premium"
        else:
            position = "In line with market"

    return {
        "product_id": str(product_id),
        "listing_count": len(competitors),
        "competitors": competitors,
        "market_median": market_median,
        "market_average": round(market_avg, 2) if market_avg is not None else None,
        "lowest_price": lowest,
        "highest_price": highest,
        "position": position,
    }


async def get_product_intelligence_summary(
    db: AsyncSession,
    product_id: UUID,
    days: int = 30,
) -> dict[str, Any]:
    """
    One-call summary that a dashboard can consume.
    Combines analytics + competitor snapshot.
    """
    analytics = await get_product_analytics(db, product_id, days=days)
    competitors = await get_competitor_snapshot(db, product_id)

    return {
        "product_id": str(product_id),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analytics": analytics,
        "competitive": competitors,
    }
