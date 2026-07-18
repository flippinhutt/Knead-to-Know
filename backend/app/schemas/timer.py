from datetime import datetime

from pydantic import BaseModel


class TimerCreate(BaseModel):
    name: str
    duration_minutes: int
    recipe_step_id: int | None = None


class TimerOut(BaseModel):
    id: int
    name: str
    duration_minutes: int
    started_at: datetime | None
    ends_at: datetime | None
    is_active: bool
    recipe_step_id: int | None

    model_config = {"from_attributes": True}
