from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


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

    @field_serializer("started_at", "ends_at")
    def _serialize_utc(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
