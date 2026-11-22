from datetime import datetime

from sqlalchemy import (
    String, Integer, ForeignKey,
    DateTime, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('IN', 'OUT')"
        ),
        CheckConstraint("quantity > 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey("inventory.id"), index=True
    )

    movement_type: Mapped[str] = mapped_column(
        String(3), nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    inventory = relationship(
        "Inventory", back_populates="movements"
    )