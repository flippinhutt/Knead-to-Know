from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recipe import Recipe, RecipeStep
from app.schemas.recipe import RecipeCreate, RecipeImportPreview, RecipeImportRequest, RecipeOut, RecipeUpdate
from app.services import ollama as ollama_service

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=list[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).all()


@router.post("/", response_model=RecipeOut, status_code=201)
def create_recipe(body: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(name=body.name, description=body.description, source=body.source)
    db.add(recipe)
    db.flush()
    for step in body.steps:
        db.add(RecipeStep(recipe_id=recipe.id, **step.model_dump()))
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.patch("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, body: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(recipe, field, value)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()


@router.post("/import", response_model=RecipeImportPreview)
async def import_recipe(body: RecipeImportRequest, db: Session = Depends(get_db)):
    """Send raw recipe text to Ollama and return parsed preview for user confirmation."""
    config = ollama_service.resolved_config(db)
    model = body.model or config["ollama_model"]
    try:
        parsed = await ollama_service.import_recipe(config["ollama_base_url"], model, body.raw_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc
    return RecipeImportPreview(**parsed)
