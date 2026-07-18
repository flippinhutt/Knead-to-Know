from datetime import datetime

from pydantic import BaseModel


class FeedingCreate(BaseModel):
    flour_grams: float | None = None
    water_grams: float | None = None
    starter_grams: float | None = None
    height_mm: int | None = None
    ambient_temp_f: int | None = None
    notes: str | None = None


class FeedingOut(FeedingCreate):
    id: int
    starter_id: int
    fed_at: datetime

    model_config = {"from_attributes": True}


class StarterCreate(BaseModel):
    name: str
    description: str | None = None
    hydration_percent: float | None = None
    feed_interval_hours: int | None = None


class StarterUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    hydration_percent: float | None = None
    feed_interval_hours: int | None = None
    archived: bool | None = None


class StarterOut(BaseModel):
    id: int
    name: str
    description: str | None
    hydration_percent: float | None
    feed_interval_hours: int | None
    archived: bool
    created_at: datetime
    feedings: list[FeedingOut] = []

    model_config = {"from_attributes": True}
