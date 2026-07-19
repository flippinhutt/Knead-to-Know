from datetime import datetime

from pydantic import BaseModel


class RecipeStepCreate(BaseModel):
    order: int
    title: str | None = None
    description: str
    duration_minutes: int | None = None


class RecipeStepOut(RecipeStepCreate):
    id: int
    recipe_id: int

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    name: str
    description: str | None = None
    source: str | None = None
    steps: list[RecipeStepCreate] = []


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    source: str | None = None


class RecipeOut(BaseModel):
    id: int
    name: str
    description: str | None
    source: str | None
    created_at: datetime
    steps: list[RecipeStepOut] = []

    model_config = {"from_attributes": True}


class RecipeStepsReplaceRequest(BaseModel):
    steps: list[RecipeStepCreate]


class RecipeImportRequest(BaseModel):
    raw_text: str = ""
    url: str | None = None
    model: str | None = None  # override default model per-request


class RecipeImportPreview(BaseModel):
    name: str
    description: str | None = None
    steps: list[RecipeStepCreate]
