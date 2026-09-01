from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ListingCreate(BaseModel):
    source: str
    url: str
    tracking_frequency_minutes: int = 120


class ListingOut(ListingCreate):
    id: UUID

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
