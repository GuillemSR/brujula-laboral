from app.ai.bedrock_client import ModelResponse
from app.rag.answering import build_cited_answer
from app.rag.chunking import SourceDocument, chunk_document
from app.rag.metadata import RagSourceMetadata
from app.rag.retrieval import RetrievalResult


def _result() -> RetrievalResult:
    source = RagSourceMetadata.model_validate(
        {
            "source_id": "fuente-test",
            "title": "Fuente test",
            "source_type": "official_guide",
            "source_url": "https://example.com/fuente",
            "publisher": "Example",
            "territory": "estatal",
            "sector": "general",
            "legal_rank": "official_guidance",
            "status": "active",
        }
    )
    document = SourceDocument(
        source_id=source.source_id,
        title=source.title,
        text="## Jornada\nContenido citado sobre jornada laboral.",
        metadata=source,
    )
    return RetrievalResult(chunk=chunk_document(document)[0], score=0.8)


def test_build_cited_answer_includes_sources_and_references() -> None:
    answer = build_cited_answer("jornada", [_result()])

    assert "[1] Fuente test, Jornada" in answer.answer
    assert answer.sources[0].title == "Fuente test"
    assert answer.sources[0].url == "https://example.com/fuente"
    assert answer.sources[0].reference == "Fuente test, Jornada"


def test_build_cited_answer_responds_without_relevant_results() -> None:
    answer = build_cited_answer("despido estando de baja", [_result()])

    assert "orientacion general" in answer.answer
    assert answer.sources == []


def test_build_cited_answer_handles_empty_results_with_single_answer() -> None:
    answer = build_cited_answer("consulta sin cobertura", [])

    assert "orientacion general" in answer.answer
    assert answer.sources == []


def test_build_cited_answer_uses_model_even_without_sources() -> None:
    calls: list[tuple[str, str]] = []

    def generate(prompt: str, system_prompt: str) -> ModelResponse:
        calls.append((prompt, system_prompt))
        return ModelResponse(text="Respuesta generada sin depender del corpus.", model_id="test")

    answer = build_cited_answer(
        "despido estando de baja",
        [],
        generate_answer=generate,
    )

    assert answer.answer == "Respuesta generada sin depender del corpus."
    assert answer.sources == []
    assert calls
    assert "no menciones esa ausencia" in calls[0][0]


def test_build_cited_answer_falls_back_when_model_fails() -> None:
    def generate(_prompt: str, _system_prompt: str) -> ModelResponse:
        raise RuntimeError("model unavailable")

    answer = build_cited_answer(
        "despido estando de baja",
        [],
        generate_answer=generate,
    )

    assert "orientacion general" in answer.answer
    assert answer.sources == []
