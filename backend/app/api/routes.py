from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("La pregunta no puede estar vacia.")
        return normalized


class Source(BaseModel):
    title: str
    url: str | None = None
    reference: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


def build_no_document_answer(question: str) -> AskResponse:
    return AskResponse(
        answer=(
            "He recibido tu consulta laboral o sindical, pero este prototipo todavia no tiene "
            "conectado el corpus RAG ni un modelo juridico. Por ahora no puedo darte una "
            "respuesta legal fiable ni citar fuentes concretas. "
            "La siguiente fase debera buscar fuentes publicas, recuperar fragmentos relevantes "
            "y generar una respuesta citada. "
            f"Consulta recibida: {question}"
        ),
        sources=[],
        limitations=[
            "Sin documento privado adjunto.",
            "Sin recuperacion RAG conectada todavia.",
            "Sin citas juridicas verificadas; no debe usarse como asesoramiento legal.",
        ],
    )


@router.post("/ask", response_model=AskResponse)
@router.post("/query", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return build_no_document_answer(request.question)
