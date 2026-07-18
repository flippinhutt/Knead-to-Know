from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_tables
from app.routers import ollama, recipes, starters, timers


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="Sourdough Tracker", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(starters.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(timers.router, prefix="/api")
app.include_router(ollama.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
