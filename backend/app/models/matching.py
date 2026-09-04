import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProductMatch(Base):
    """
    Links two products that are believed to be the same real-world item
    (or close variants). Always stores a confidence score.
    """

    __tablename__ = "product_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    product_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="fuzzy+rules")  # fuzzy, embedding, hybrid
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
