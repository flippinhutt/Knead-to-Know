from datetime import datetime

from pydantic import BaseModel


class BakeCreate(BaseModel):
    starter_id: int | None = None
    recipe_id: int | None = None
    hydration_percent: float | None = None
    oven_temp_f: int | None = None
    outcome: str | None = None
    notes: str | None = None


class BakeOut(BakeCreate):
    id: int
    baked_at: datetime

    model_config = {"from_attributes": True}
