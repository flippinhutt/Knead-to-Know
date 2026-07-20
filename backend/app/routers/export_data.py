from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.bake import Bake
from app.models.feeding import Feeding
from app.models.recipe import Recipe
from app.models.starter import Starter

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/")
def export_all(db: Session = Depends(get_db)):
    starters = db.query(Starter).all()
    recipes = db.query(Recipe).all()
    bakes = db.query(Bake).all()

    data = {
        "starters": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "hydration_percent": s.hydration_percent,
                "feed_interval_hours": s.feed_interval_hours,
                "created_at": s.created_at.isoformat(),
                "feedings": [
                    {
                        "id": f.id,
                        "fed_at": f.fed_at.isoformat(),
                        "flour_grams": f.flour_grams,
                        "water_grams": f.water_grams,
                        "starter_grams": f.starter_grams,
                        "height_mm": f.height_mm,
                        "ambient_temp_f": f.ambient_temp_f,
                        "notes": f.notes,
                    }
                    for f in db.query(Feeding).filter(Feeding.starter_id == s.id).all()
                ],
            }
            for s in starters
        ],
        "recipes": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "source": r.source,
                "image_url": r.image_url,
                "created_at": r.created_at.isoformat(),
                "steps": [
                    {
                        "order": step.order,
                        "description": step.description,
                        "duration_minutes": step.duration_minutes,
                    }
                    for step in r.steps
                ],
                "ingredients": [
                    {
                        "order": ing.order,
                        "name": ing.name,
                        "amount": ing.amount,
                    }
                    for ing in r.ingredients
                ],
            }
            for r in recipes
        ],
        "bakes": [
            {
                "id": b.id,
                "starter_id": b.starter_id,
                "recipe_id": b.recipe_id,
                "baked_at": b.baked_at.isoformat(),
                "hydration_percent": b.hydration_percent,
                "oven_temp_f": b.oven_temp_f,
                "outcome": b.outcome,
                "notes": b.notes,
            }
            for b in bakes
        ],
    }

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": "attachment; filename=knead-to-know-export.json"},
    )
