from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CheckoutRequest(BaseModel):
    plan: str  # "professional" | "enterprise"


class CheckoutResponse(BaseModel):
    checkout_url: str


class SubscriptionOut(BaseModel):
    id: UUID
    plan: str
    status: str
    current_period_end: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
