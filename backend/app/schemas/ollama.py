from pydantic import BaseModel


class OllamaModel(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None


class OllamaConfig(BaseModel):
    ollama_base_url: str
    ollama_model: str


class OllamaConfigUpdate(BaseModel):
    ollama_base_url: str | None = None
    ollama_model: str | None = None


class PullRequest(BaseModel):
    model: str
