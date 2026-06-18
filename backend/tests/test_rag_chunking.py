from app.rag.chunking import SourceDocument, chunk_document
from app.rag.metadata import RagSourceMetadata


def _metadata() -> RagSourceMetadata:
    return RagSourceMetadata.model_validate(
        {
            "source_id": "fuente-test",
            "title": "Fuente test",
            "source_type": "legislation",
            "source_url": "https://example.com/fuente",
            "publisher": "Example",
            "territory": "estatal",
            "sector": "general",
            "legal_rank": "law",
            "status": "active",
        }
    )


def test_chunk_document_splits_markdown_headings() -> None:
    document = SourceDocument(
        source_id="fuente-test",
        title="Fuente test",
        text="# Titulo inicial\nTexto inicial.\n\n## Jornada\nTexto de jornada.",
        metadata=_metadata(),
    )

    chunks = chunk_document(document)

    assert [chunk.section for chunk in chunks] == ["Titulo inicial", "Jornada"]
    assert chunks[0].chunk_id == "fuente-test:0"
    assert chunks[1].citation_label == "Fuente test, Jornada"


def test_chunk_document_splits_articles_and_clauses() -> None:
    document = SourceDocument(
        source_id="fuente-test",
        title="Fuente test",
        text="Articulo 1. Ambito\nTexto articulo.\n\nClausula 2. Jornada\nTexto clausula.",
        metadata=_metadata(),
    )

    chunks = chunk_document(document)

    assert [chunk.section for chunk in chunks] == ["Articulo 1. Ambito", "Clausula 2. Jornada"]
    assert "Texto articulo." in chunks[0].text
    assert "Texto clausula." in chunks[1].text


def test_chunk_document_uses_full_document_when_no_section_is_found() -> None:
    document = SourceDocument(
        source_id="fuente-test",
        title="Fuente test",
        text="Texto sin encabezados juridicos.",
        metadata=_metadata(),
    )

    chunks = chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].section == "documento-completo"


def test_chunk_document_truncates_long_section_labels() -> None:
    source = _metadata()
    long_heading = "## " + "Apartado muy largo " * 20
    document = SourceDocument(
        source_id="fuente-test",
        title="Fuente test",
        text=f"{long_heading}\nContenido.",
        metadata=source,
    )

    chunk = chunk_document(document)[0]

    assert len(chunk.section) <= 200
    assert chunk.section.endswith("...")
    assert chunk.metadata.section == chunk.section
