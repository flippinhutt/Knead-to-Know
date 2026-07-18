from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.models.bake import Bake
from app.models.feeding import Feeding
from app.models.recipe import Recipe, RecipeStep
from app.models.starter import Starter

router = APIRouter(prefix="/import", tags=["import"])


class ImportFeeding(BaseModel):
    id: int
    fed_at: str
    flour_grams: float | None = None
    water_grams: float | None = None
    starter_grams: float | None = None
    height_mm: int | None = None
    ambient_temp_f: int | None = None
    notes: str | None = None


class ImportStarter(BaseModel):
    id: int
    name: str
    description: str | None = None
    hydration_percent: float | None = None
    feed_interval_hours: int | None = None
    feedings: list[ImportFeeding] = []


class ImportStep(BaseModel):
    order: int
    description: str
    duration_minutes: int | None = None


class ImportRecipe(BaseModel):
    id: int
    name: str
    description: str | None = None
    source: str | None = None
    steps: list[ImportStep] = []


class ImportBake(BaseModel):
    id: int
    starter_id: int | None = None
    recipe_id: int | None = None
    baked_at: str
    hydration_percent: float | None = None
    oven_temp_f: int | None = None
    outcome: str | None = None
    notes: str | None = None


class ImportPayload(BaseModel):
    starters: list[ImportStarter] = []
    recipes: list[ImportRecipe] = []
    bakes: list[ImportBake] = []


@router.post("/")
def import_all(body: ImportPayload, db: Session = Depends(get_db)):
    starter_id_map: dict[int, int] = {}
    recipe_id_map: dict[int, int] = {}

    for s in body.starters:
        starter = Starter(
            name=s.name,
            description=s.description,
            hydration_percent=s.hydration_percent,
            feed_interval_hours=s.feed_interval_hours,
        )
        db.add(starter)
        db.flush()
        starter_id_map[s.id] = starter.id
        for f in s.feedings:
            db.add(Feeding(
                starter_id=starter.id,
                fed_at=datetime.fromisoformat(f.fed_at),
                flour_grams=f.flour_grams,
                water_grams=f.water_grams,
                starter_grams=f.starter_grams,
                height_mm=f.height_mm,
                ambient_temp_f=f.ambient_temp_f,
                notes=f.notes,
            ))

    for r in body.recipes:
        recipe = Recipe(name=r.name, description=r.description, source=r.source)
        db.add(recipe)
        db.flush()
        recipe_id_map[r.id] = recipe.id
        for step in r.steps:
            db.add(RecipeStep(
                recipe_id=recipe.id,
                order=step.order,
                description=step.description,
                duration_minutes=step.duration_minutes,
            ))

    for b in body.bakes:
        db.add(Bake(
            starter_id=starter_id_map.get(b.starter_id) if b.starter_id else None,
            recipe_id=recipe_id_map.get(b.recipe_id) if b.recipe_id else None,
            baked_at=datetime.fromisoformat(b.baked_at),
            hydration_percent=b.hydration_percent,
            oven_temp_f=b.oven_temp_f,
            outcome=b.outcome,
            notes=b.notes,
        ))

    db.commit()
    return JSONResponse({"imported": {
        "starters": len(body.starters),
        "recipes": len(body.recipes),
        "bakes": len(body.bakes),
    }})
