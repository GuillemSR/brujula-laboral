from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class Source(BaseModel):
    title: str
    url: str | None = None
    reference: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    limitations: list[str] = []


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return AskResponse(
        answer=(
            "Endpoint preparado. Falta conectar retrieval RAG y Bedrock. "
            f"Pregunta recibida: {request.question}"
        ),
        limitations=["Prototipo sin respuesta juridica real todavia."],
    )
