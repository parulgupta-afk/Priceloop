import enum
import uuid
from datetime import datetime
# pyrefly: ignore [missing-import]  
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String, Text

# pyrefly: ignore [missing-import]
from sqlalchemy.dialects.postgresql import JSONB, UUID

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship, synonym

from app.models.base import Base


class AvailabilityStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN = "UNKNOWN"
    PREORDER = "PREORDER"


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    base_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    rate_limit_per_second = Column(Numeric(5, 2), default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    listings = relationship("ProductListing", back_populates="source_rel")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(500), nullable=False)
    brand = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    sku = Column(String(100), nullable=True)
    gtin = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    attributes = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_id = synonym("user_id")

    listings = relationship("ProductListing", back_populates="product", cascade="all, delete-orphan")


class ProductListing(Base):
    __tablename__ = "product_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True)
    external_url = Column("external_url", String(1000), nullable=False)
    external_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    current_price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    availability = Column(String(12), default=AvailabilityStatus.IN_STOCK.value, nullable=False)
    match_confidence = Column(Numeric(4, 3), nullable=True)
    last_scraped_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    url = synonym("external_url")

    @property
    def source(self) -> str:
        return self.source_rel.name if self.source_rel else "demo"

    @property
    def tracking_frequency_minutes(self) -> int:
        return 120

    product = relationship("Product", back_populates="listings")
    source_rel = relationship("Source", back_populates="listings")
    observations = relationship("PriceObservation", back_populates="listing", cascade="all, delete-orphan")


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("product_listings.id"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    availability = Column(String(12), default=AvailabilityStatus.IN_STOCK.value, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_data = Column(JSONB, nullable=True)

    listing = relationship("ProductListing", back_populates="observations")
