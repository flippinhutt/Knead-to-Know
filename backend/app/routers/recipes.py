import json
from html.parser import HTMLParser

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recipe import Recipe, RecipeIngredient, RecipeStep
from app.schemas.recipe import (
    RecipeCreate,
    RecipeImportPreview,
    RecipeImportRequest,
    RecipeIngredientsReplaceRequest,
    RecipeOut,
    RecipeStepsReplaceRequest,
    RecipeUpdate,
)
from app.services import ollama as ollama_service


class _TextExtractor(HTMLParser):
    _SKIP = {"script", "style", "nav", "header", "footer", "aside", "noscript"}
    _HEADINGS = {"h1", "h2", "h3"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._depth = 0
        self._current_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in self._SKIP:
            self._depth += 1
        self._current_tag = tag

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._depth > 0:
            self._depth -= 1
        if tag == self._current_tag:
            self._current_tag = None

    def handle_data(self, data: str) -> None:
        if self._depth == 0:
            stripped = data.strip()
            if stripped:
                if self._current_tag in self._HEADINGS:
                    self._parts.append(f"## {stripped}")
                else:
                    self._parts.append(stripped)

    def text(self) -> str:
        return "\n".join(self._parts)


class _JsonLdExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_jsonld = False
        self._buf = ""
        self._blobs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._in_jsonld = True
            self._buf = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_jsonld:
            self._blobs.append(self._buf)
            self._in_jsonld = False

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._buf += data


def _extract_recipe_from_json_ld(html: str) -> str | None:
    parser = _JsonLdExtractor()
    try:
        parser.feed(html)
    except Exception:
        return None
    for blob in parser._blobs:
        try:
            data = json.loads(blob)
        except Exception:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            rtype = item.get("@type", "")
            types = rtype if isinstance(rtype, list) else [rtype]
            if "Recipe" not in types:
                continue
            parts: list[str] = []
            if name := item.get("name"):
                parts.append(f"Recipe: {name}")
            if desc := item.get("description"):
                parts.append(f"Description: {desc}")
            ingredients = item.get("recipeIngredient") or item.get("ingredients") or []
            if ingredients:
                parts.append("Ingredients:")
                for ing in ingredients:
                    if isinstance(ing, str) and ing.strip():
                        parts.append(f"- {ing.strip()}")
            for i, step in enumerate(item.get("recipeInstructions", []), 1):
                if isinstance(step, str):
                    parts.append(f"{i}. {step}")
                elif isinstance(step, dict):
                    text = step.get("text") or step.get("name") or ""
                    if text:
                        parts.append(f"{i}. {text}")
            if parts:
                return "\n".join(parts)
    return None


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
    for ingredient in body.ingredients:
        db.add(RecipeIngredient(recipe_id=recipe.id, **ingredient.model_dump()))
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


@router.put("/{recipe_id}/steps", response_model=RecipeOut)
def replace_steps(recipe_id: int, body: RecipeStepsReplaceRequest, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.query(RecipeStep).filter(RecipeStep.recipe_id == recipe_id).delete()
    for step in body.steps:
        db.add(RecipeStep(recipe_id=recipe_id, **step.model_dump()))
    db.commit()
    db.refresh(recipe)
    return recipe


@router.put("/{recipe_id}/ingredients", response_model=RecipeOut)
def replace_ingredients(recipe_id: int, body: RecipeIngredientsReplaceRequest, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).delete()
    for ingredient in body.ingredients:
        db.add(RecipeIngredient(recipe_id=recipe_id, **ingredient.model_dump()))
    db.commit()
    db.refresh(recipe)
    return recipe


@router.post("/import", response_model=RecipeImportPreview)
async def import_recipe(body: RecipeImportRequest, db: Session = Depends(get_db)):
    raw_text = body.raw_text

    if body.url:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                r = await client.get(
                    body.url,
                    timeout=15.0,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; KneadToKnow/1.0)"},
                )
                r.raise_for_status()
            raw_text = _extract_recipe_from_json_ld(r.text) or ""
            if not raw_text:
                extractor = _TextExtractor()
                extractor.feed(r.text)
                raw_text = extractor.text()
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}") from exc

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Provide raw_text or a valid url")

    config = ollama_service.resolved_config(db)
    model = body.model or config["ollama_model"]
    try:
        parsed = await ollama_service.import_recipe(config["ollama_base_url"], model, raw_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc
    try:
        return RecipeImportPreview(**parsed)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama returned unexpected recipe shape: {exc}") from exc
