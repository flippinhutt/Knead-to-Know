from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Starter(Base):
    __tablename__ = "starters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    hydration_percent: Mapped[float | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    feedings: Mapped[list["Feeding"]] = relationship(  # noqa: F821
        back_populates="starter",
        cascade="all, delete-orphan",
        order_by="Feeding.fed_at.desc()",
    )
