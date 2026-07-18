from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Feeding(Base):
    __tablename__ = "feedings"

    id: Mapped[int] = mapped_column(primary_key=True)
    starter_id: Mapped[int] = mapped_column(ForeignKey("starters.id"), nullable=False)
    fed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    flour_grams: Mapped[float | None]
    water_grams: Mapped[float | None]
    starter_grams: Mapped[float | None]
    height_mm: Mapped[int | None]
    notes: Mapped[str | None] = mapped_column(String(500))

    starter: Mapped["Starter"] = relationship(back_populates="feedings")  # noqa: F821
