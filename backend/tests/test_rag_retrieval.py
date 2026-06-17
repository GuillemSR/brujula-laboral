from pathlib import Path

from app.rag.chunking import SourceDocument, chunk_document
from app.rag.metadata import RagSourceMetadata
from app.rag.retrieval import LocalRetriever, build_local_retriever


def _metadata(source_id: str, title: str) -> RagSourceMetadata:
    return RagSourceMetadata.model_validate(
        {
            "source_id": source_id,
            "title": title,
            "source_type": "official_guide",
            "source_url": f"https://example.com/{source_id}",
            "publisher": "Example",
            "territory": "estatal",
            "sector": "general",
            "legal_rank": "official_guidance",
            "status": "active",
        }
    )


def test_local_retriever_returns_most_relevant_chunk_first() -> None:
    jornada = SourceDocument(
        source_id="jornada",
        title="Jornada",
        text="## Horas extra\nLas horas extra se regulan en la jornada laboral.",
        metadata=_metadata("jornada", "Jornada"),
    )
    sindicato = SourceDocument(
        source_id="sindicato",
        title="Sindicato",
        text="## Afiliacion sindical\nLa afiliacion sindical es un dato protegido.",
        metadata=_metadata("sindicato", "Sindicato"),
    )
    chunks = [chunk for document in [jornada, sindicato] for chunk in chunk_document(document)]
    retriever = LocalRetriever(chunks)

    results = retriever.search("horas extra jornada", top_k=1)

    assert len(results) == 1
    assert results[0].chunk.source_id == "jornada"
    assert results[0].score > 0


def test_local_retriever_respects_top_k() -> None:
    document = SourceDocument(
        source_id="jornada",
        title="Jornada",
        text="## Uno\nTexto uno.\n\n## Dos\nTexto dos.",
        metadata=_metadata("jornada", "Jornada"),
    )
    retriever = LocalRetriever(chunk_document(document))

    assert retriever.search("texto", top_k=0) == []
    assert len(retriever.search("texto", top_k=1)) == 1


def test_build_local_retriever_from_example_manifest() -> None:
    retriever = build_local_retriever(Path("corpus/sources.example.json"))

    results = retriever.search("registro jornada", top_k=2)

    assert len(results) == 2
    assert all(result.chunk.text for result in results)


def test_example_manifest_retrieves_downloaded_remote_work_source() -> None:
    retriever = build_local_retriever(Path("corpus/sources.example.json"))

    results = retriever.search("teletrabajo trabajo a distancia acuerdo", top_k=3)

    assert any(result.chunk.source_id == "boe-ley-trabajo-distancia" for result in results)
