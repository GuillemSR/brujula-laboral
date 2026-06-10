from pathlib import Path
from typing import Callable

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.documents.extraction import DocumentExtractionError, extract_text
from app.documents.temporary_context import build_temporary_context
from app.documents.uploads import DocumentUploadError, validate_upload
from app.rag.answering import build_cited_answer
from app.rag.retrieval import build_local_retriever
from app.storage.s3_temporary import S3TemporaryStorage

router = APIRouter()
TEMPORARY_CONTEXT_SEARCH_CHARS = 20_000


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_id: str | None = Field(
        default=None,
        min_length=32,
        max_length=32,
        pattern=r"^[a-f0-9]{32}$",
    )

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


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    expires_in_minutes: int


class DocumentDeleteResponse(BaseModel):
    deleted: bool


def get_temporary_storage() -> S3TemporaryStorage:
    return S3TemporaryStorage()


def get_temporary_storage_factory() -> Callable[[], S3TemporaryStorage]:
    return S3TemporaryStorage


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    storage: S3TemporaryStorage = Depends(get_temporary_storage),
) -> DocumentUploadResponse:
    settings = get_settings()
    content = await file.read()
    try:
        upload = validate_upload(file.filename, file.content_type, content, settings)
        stored = storage.put_document(
            document_id=upload.document_id,
            content=upload.content,
            content_type=upload.content_type,
        )
    except DocumentUploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return DocumentUploadResponse(
        document_id=stored.document_id,
        filename=upload.filename,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        expires_in_minutes=settings.temp_document_ttl_minutes,
    )


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(
    document_id: str,
    storage: S3TemporaryStorage = Depends(get_temporary_storage),
) -> DocumentDeleteResponse:
    try:
        storage.delete_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Documento temporal no encontrado.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DocumentDeleteResponse(deleted=True)


@router.post("/ask", response_model=AskResponse)
@router.post("/query", response_model=AskResponse)
def ask(
    request: AskRequest,
    storage_factory: Callable[[], S3TemporaryStorage] = Depends(get_temporary_storage_factory),
) -> AskResponse:
    settings = get_settings()
    search_query = request.question
    used_temporary_document = False

    if request.document_id:
        storage = storage_factory()
        try:
            temporary_document = storage.get_document(request.document_id)
            extracted = extract_text(
                filename="documento-temporal",
                content=temporary_document.content,
                content_type=temporary_document.content_type,
            )
        except DocumentExtractionError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail="Documento temporal no encontrado o expirado. Vuelve a subirlo.",
            ) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        temporary_context = build_temporary_context(extracted.filename, extracted.text)
        search_query = (
            f"{request.question}\n\n{temporary_context.text[:TEMPORARY_CONTEXT_SEARCH_CHARS]}"
        )
        used_temporary_document = True

    retriever = build_local_retriever(manifest_path=Path("corpus/sources.example.json"))
    results = [
        result
        for result in retriever.search(search_query, top_k=settings.rag_top_k)
        if result.score >= settings.rag_min_score
    ]
    cited_answer = build_cited_answer(request.question, results)
    limitations = list(cited_answer.limitations)
    if used_temporary_document:
        limitations.append(
            "Documento privado temporal extraido solo en memoria y no anadido al indice RAG."
        )

    return AskResponse(
        answer=cited_answer.answer,
        sources=[
            Source(title=source.title, url=source.url, reference=source.reference)
            for source in cited_answer.sources
        ],
        limitations=limitations,
    )
