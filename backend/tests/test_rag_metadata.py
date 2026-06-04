import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.rag.chunking import SourceDocument, chunk_document
from app.rag.metadata import RagSourceMetadata, SourceType, load_source_manifest


def test_example_source_manifest_loads() -> None:
    sources = load_source_manifest(Path("corpus/sources.example.json"))

    assert len(sources) == 3
    assert sources[0].source_id == "boe-estatuto-trabajadores"
    assert sources[0].source_type == SourceType.LEGISLATION


def test_manifest_requires_core_fields(tmp_path: Path) -> None:
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps([{"source_id": "missing-fields"}]), encoding="utf-8")

    with pytest.raises(ValidationError) as error:
        load_source_manifest(manifest)

    error_text = str(error.value)
    assert "title" in error_text
    assert "source_type" in error_text
    assert "source_url" in error_text


def test_manifest_rejects_unknown_enums(tmp_path: Path) -> None:
    manifest = tmp_path / "sources.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "source_id": "fuente-test",
                    "title": "Fuente test",
                    "source_type": "blog",
                    "source_url": "https://example.com/fuente",
                    "publisher": "Example",
                    "territory": "estatal",
                    "sector": "general",
                    "legal_rank": "law",
                    "status": "active",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError) as error:
        load_source_manifest(manifest)

    assert "source_type" in str(error.value)


def test_manifest_rejects_duplicate_source_ids(tmp_path: Path) -> None:
    source = {
        "source_id": "fuente-duplicada",
        "title": "Fuente duplicada",
        "source_type": "official_guide",
        "source_url": "https://example.com/fuente",
        "publisher": "Example",
        "territory": "estatal",
        "sector": "general",
        "legal_rank": "official_guidance",
        "status": "pending_review",
    }
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps([source, source]), encoding="utf-8")

    with pytest.raises(ValueError, match="source_id duplicado: fuente-duplicada"):
        load_source_manifest(manifest)


def test_chunk_metadata_inherits_citation_fields() -> None:
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
        text="Contenido de prueba.",
        metadata=source,
    )

    chunks = chunk_document(document)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.chunk_id == "fuente-test:0"
    assert chunk.section == "documento-completo"
    assert chunk.citation_label == "Fuente test, documento-completo"
    assert chunk.metadata.source.source_url.unicode_string() == "https://example.com/fuente"
    assert chunk.metadata.source.legal_rank == "official_guidance"
