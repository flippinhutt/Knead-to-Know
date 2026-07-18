from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.setting import Setting
from app.schemas.ollama import OllamaConfig, OllamaConfigUpdate, OllamaModel, PullRequest
from app.services import ollama as ollama_service

router = APIRouter(prefix="/ollama", tags=["ollama"])


@router.get("/config", response_model=OllamaConfig)
def get_config(db: Session = Depends(get_db)):
    return OllamaConfig(**ollama_service.resolved_config(db))


@router.patch("/config", response_model=OllamaConfig)
def update_config(body: OllamaConfigUpdate, db: Session = Depends(get_db)):
    """Persist Ollama URL/model overrides to SQLite. Survives restarts."""
    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        row = db.get(Setting, key)
        if row:
            row.value = value
        else:
            db.add(Setting(key=key, value=value))
    db.commit()
    return OllamaConfig(**ollama_service.resolved_config(db))


@router.get("/models", response_model=list[OllamaModel])
async def list_models(db: Session = Depends(get_db)):
    """List models currently available on the Ollama server."""
    config = ollama_service.resolved_config(db)
    try:
        models = await ollama_service.list_models(config["ollama_base_url"])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cannot reach Ollama: {exc}") from exc
    return [OllamaModel(**m) for m in models]


@router.post("/pull")
async def pull_model(body: PullRequest, db: Session = Depends(get_db)):
    """Pull a model from Ollama registry. Streams progress as newline-delimited JSON."""
    config = ollama_service.resolved_config(db)

    async def stream():
        try:
            async for chunk in ollama_service.pull_model(config["ollama_base_url"], body.model):
                yield chunk + "\n"
        except Exception as exc:
            yield f'{{"error": "{exc}"}}\n'

    return StreamingResponse(stream(), media_type="application/x-ndjson")
