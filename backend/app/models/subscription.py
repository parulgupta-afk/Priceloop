import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class PlanTier(str, enum.Enum):
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, enum.Enum):
    NONE = "NONE"  # never subscribed -- on the free tier
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"


class Subscription(Base):
    """
    One row per user, updated by Stripe webhook events -- never by the
    checkout endpoint directly. The checkout endpoint only creates a Stripe
    Checkout Session and hands the user a URL to pay at; the row here only
    reflects reality once Stripe confirms payment via webhook. This is the
    standard pattern: never mark something "paid" client-side or at
    session-creation time, since the user might close the tab before paying.
    """

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    plan = Column(Enum(PlanTier), default=PlanTier.FREE, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.NONE, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
