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


def test_build_cited_answer_handles_empty_results() -> None:
    answer = build_cited_answer("consulta sin cobertura", [])

    assert "No he encontrado fuentes" in answer.answer
    assert answer.sources == []
