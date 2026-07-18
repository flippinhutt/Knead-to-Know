from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Bake(Base):
    __tablename__ = "bakes"

    id: Mapped[int] = mapped_column(primary_key=True)
    starter_id: Mapped[int | None] = mapped_column(ForeignKey("starters.id"), nullable=True)
    recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id"), nullable=True)
    baked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    hydration_percent: Mapped[float | None]
    oven_temp_f: Mapped[int | None] = mapped_column(Integer)
    outcome: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
