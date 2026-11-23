
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from .user import User


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # NEW: Warehouse owner
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Existing relationship
    users: Mapped[list[User]] = relationship(
        back_populates="warehouse",
        foreign_keys="User.warehouse_id",
    )

    # NEW: Owner relationship
    owner: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[owner_id],
    )
    
