from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.rag.answering import build_cited_answer
from app.rag.retrieval import build_local_retriever

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


@router.post("/ask", response_model=AskResponse)
@router.post("/query", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    settings = get_settings()
    retriever = build_local_retriever(manifest_path=Path("corpus/sources.example.json"))
    results = [
        result
        for result in retriever.search(request.question, top_k=settings.rag_top_k)
        if result.score >= settings.rag_min_score
    ]
    cited_answer = build_cited_answer(request.question, results)
    return AskResponse(
        answer=cited_answer.answer,
        sources=[
            Source(title=source.title, url=source.url, reference=source.reference)
            for source in cited_answer.sources
        ],
        limitations=cited_answer.limitations,
    )
