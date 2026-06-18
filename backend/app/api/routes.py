import json
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator
from starlette.responses import StreamingResponse

from app.ai.bedrock_client import BedrockClient, ModelResponse
from app.ai.mock_bedrock import MockBedrockRuntimeClient
from app.ai.ollama_client import OllamaClient
from app.core.config import Settings, get_settings
from app.documents.extraction import DocumentExtractionError, extract_text
from app.documents.temporary_context import build_temporary_context
from app.documents.uploads import DocumentUploadError, validate_upload
from app.rag.answering import SYSTEM_PROMPT, build_answer_context, build_cited_answer
from app.rag.retrieval import RetrievalResult, build_local_retriever
from app.storage.local import InMemoryTemporaryDocumentStorage
from app.storage.s3_temporary import S3TemporaryStorage

router = APIRouter()
TEMPORARY_CONTEXT_SEARCH_CHARS = 20_000
DEFAULT_MOCK_MODEL_ID = "mock.amazon.nova-micro-v1:0"
TEMPORARY_STORAGE_UNAVAILABLE_DETAIL = (
    "Servicio temporal de documentos no disponible. Intentalo de nuevo mas tarde."
)


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


@dataclass(frozen=True)
class AnswerInputs:
    search_query: str
    private_context: str | None
    used_temporary_document: bool
    results: list[RetrievalResult]


TemporaryStorage = S3TemporaryStorage | InMemoryTemporaryDocumentStorage


@lru_cache
def get_local_temporary_storage(temp_document_ttl_minutes: int) -> InMemoryTemporaryDocumentStorage:
    return InMemoryTemporaryDocumentStorage(
        settings=Settings(temp_document_ttl_minutes=temp_document_ttl_minutes)
    )


def get_temporary_storage() -> TemporaryStorage:
    settings = get_settings()
    if _should_use_local_temporary_storage(settings):
        return get_local_temporary_storage(settings.temp_document_ttl_minutes)

    try:
        return S3TemporaryStorage()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=TEMPORARY_STORAGE_UNAVAILABLE_DETAIL) from exc


def get_temporary_storage_factory() -> Callable[[], TemporaryStorage]:
    def build_storage() -> TemporaryStorage:
        settings = get_settings()
        if _should_use_local_temporary_storage(settings):
            return get_local_temporary_storage(settings.temp_document_ttl_minutes)

        try:
            return S3TemporaryStorage()
        except Exception as exc:
            raise RuntimeError("Temporary storage unavailable") from exc

    return build_storage


def _should_use_local_temporary_storage(settings: Settings) -> bool:
    if settings.temp_document_storage == "memory":
        return True
    if settings.temp_document_storage == "s3":
        return False
    return settings.ai_provider == "ollama" or not settings.s3_temp_bucket


def get_answer_generator() -> Callable[[str, str], ModelResponse] | None:
    settings = get_settings()
    if settings.ai_provider == "mock":
        mock_settings = (
            settings
            if settings.bedrock_model_id
            else settings.model_copy(update={"bedrock_model_id": DEFAULT_MOCK_MODEL_ID})
        )
        return BedrockClient(client=MockBedrockRuntimeClient(), settings=mock_settings).generate

    if settings.ai_provider == "ollama":
        return OllamaClient(settings=settings).generate

    if not settings.bedrock_model_id:
        return None
    try:
        return BedrockClient(settings=settings).generate
    except Exception:
        return None


def get_streaming_answer_generator() -> Callable[[str, str], Iterator[str]] | None:
    settings = get_settings()
    if settings.ai_provider == "ollama":
        return OllamaClient(settings=settings).stream
    return None


def _build_answer_inputs(
    request: AskRequest,
    storage_factory: Callable[[], TemporaryStorage],
) -> AnswerInputs:
    settings = get_settings()
    search_query = request.question
    private_context: str | None = None
    used_temporary_document = False

    if request.document_id:
        try:
            storage = storage_factory()
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
            raise HTTPException(
                status_code=503, detail=TEMPORARY_STORAGE_UNAVAILABLE_DETAIL
            ) from exc

        temporary_context = build_temporary_context(extracted.filename, extracted.text)
        search_query = (
            f"{request.question}\n\n{temporary_context.text[:TEMPORARY_CONTEXT_SEARCH_CHARS]}"
        )
        private_context = temporary_context.text[:TEMPORARY_CONTEXT_SEARCH_CHARS]
        used_temporary_document = True

    retriever = build_local_retriever(manifest_path=Path("corpus/sources.example.json"))
    results = [
        result
        for result in retriever.search(search_query, top_k=settings.rag_top_k)
        if result.score >= settings.rag_min_score
    ]
    return AnswerInputs(
        search_query=search_query,
        private_context=private_context,
        used_temporary_document=used_temporary_document,
        results=results,
    )


def _line_event(event_type: str, **payload: object) -> str:
    return json.dumps({"type": event_type, **payload}, ensure_ascii=False) + "\n"


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    storage: TemporaryStorage = Depends(get_temporary_storage),
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
        raise HTTPException(status_code=503, detail=TEMPORARY_STORAGE_UNAVAILABLE_DETAIL) from exc

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
    storage: TemporaryStorage = Depends(get_temporary_storage),
) -> DocumentDeleteResponse:
    try:
        storage.delete_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Documento temporal no encontrado.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=TEMPORARY_STORAGE_UNAVAILABLE_DETAIL) from exc
    return DocumentDeleteResponse(deleted=True)


@router.post("/ask", response_model=AskResponse)
@router.post("/query", response_model=AskResponse)
def ask(
    request: AskRequest,
    storage_factory: Callable[[], TemporaryStorage] = Depends(get_temporary_storage_factory),
    answer_generator: Callable[[str, str], ModelResponse] | None = Depends(get_answer_generator),
) -> AskResponse:
    answer_inputs = _build_answer_inputs(request, storage_factory)
    cited_answer = build_cited_answer(
        question=request.question,
        results=answer_inputs.results,
        relevance_query=answer_inputs.search_query,
        private_context=answer_inputs.private_context,
        generate_answer=answer_generator,
    )
    limitations = list(cited_answer.limitations)
    if answer_inputs.used_temporary_document:
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


@router.post("/ask/stream")
def ask_stream(
    request: AskRequest,
    storage_factory: Callable[[], TemporaryStorage] = Depends(get_temporary_storage_factory),
    stream_answer: Callable[[str, str], Iterator[str]] | None = Depends(
        get_streaming_answer_generator
    ),
) -> StreamingResponse:
    answer_inputs = _build_answer_inputs(request, storage_factory)
    context = build_answer_context(
        question=request.question,
        results=answer_inputs.results,
        relevance_query=answer_inputs.search_query,
        private_context=answer_inputs.private_context,
    )
    limitations = list(context.limitations)
    if answer_inputs.used_temporary_document:
        limitations.append(
            "Documento privado temporal extraido solo en memoria y no anadido al indice RAG."
        )

    sources = [
        Source(title=source.title, url=source.url, reference=source.reference).model_dump()
        for source in context.sources
    ]

    def events() -> Iterator[str]:
        yield _line_event("meta", sources=sources, limitations=limitations)

        if not stream_answer:
            cited_answer = build_cited_answer(
                question=request.question,
                results=answer_inputs.results,
                relevance_query=answer_inputs.search_query,
                private_context=answer_inputs.private_context,
                generate_answer=None,
            )
            yield _line_event("chunk", text=cited_answer.answer)
            yield _line_event("done")
            return

        try:
            emitted = False
            for text in stream_answer(context.prompt, SYSTEM_PROMPT):
                emitted = True
                yield _line_event("chunk", text=text)
            if not emitted:
                fallback = build_cited_answer(
                    question=request.question,
                    results=answer_inputs.results,
                    relevance_query=answer_inputs.search_query,
                    private_context=answer_inputs.private_context,
                    generate_answer=None,
                )
                yield _line_event("chunk", text=fallback.answer)
            yield _line_event("done")
        except RuntimeError:
            yield _line_event(
                "error",
                detail="No se pudo completar la respuesta en streaming.",
            )

    return StreamingResponse(events(), media_type="application/x-ndjson")
