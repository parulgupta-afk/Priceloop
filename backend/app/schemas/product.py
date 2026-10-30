from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ListingCreate(BaseModel):
    source: str
    url: str
    tracking_frequency_minutes: int = 120


class ListingOut(ListingCreate):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    listings: List[ListingCreate] = []


class ProductOut(BaseModel):
    id: UUID
    name: str
    brand: Optional[str]
    category: Optional[str]
    created_at: datetime
    listings: List[ListingOut] = []

    model_config = ConfigDict(from_attributes=True)


class PriceObservationOut(BaseModel):
    id: UUID
    listing_id: UUID
    price: float
    currency: str
    availability: str
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)
