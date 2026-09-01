import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("ProductListing", back_populates="product", cascade="all, delete-orphan")


class ProductListing(Base):
    __tablename__ = "product_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    source = Column(String, nullable=False)  # e.g. "amazon", "walmart"
    url = Column(String, nullable=False)
    tracking_frequency_minutes = Column(Integer, default=120)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="listings")
