from datetime import datetime

from sqlalchemy import (
    Integer, ForeignKey, DateTime,
    UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "warehouse_id", "product_id",
            name="uq_inventory_warehouse_product"
        ),
        CheckConstraint("quantity >= 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id"), index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), index=True
    )

    quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    warehouse = relationship("Warehouse")
    product = relationship("Product")

    movements = relationship(
        "StockMovement", back_populates="inventory"
    )