import json
from pathlib import Path

import pytest

from app.rag.ingest import ingest_corpus_manifest
from app.rag.loader import load_corpus


def _source(content_path: str) -> dict[str, str]:
    return {
        "source_id": "fuente-test",
        "title": "Fuente test",
        "source_type": "official_guide",
        "source_url": "https://example.com/fuente",
        "publisher": "Example",
        "territory": "estatal",
        "sector": "general",
        "legal_rank": "official_guidance",
        "status": "active",
        "content_path": content_path,
    }


def test_load_corpus_loads_example_manifest() -> None:
    corpus = load_corpus(Path("corpus/sources.example.json"))

    assert len(corpus.documents) == 3
    assert corpus.documents[0].source_id == "boe-estatuto-trabajadores"
    assert "Estatuto de los Trabajadores" in corpus.documents[0].text


def test_ingest_corpus_manifest_returns_chunk_count() -> None:
    chunk_count = ingest_corpus_manifest("corpus/sources.example.json")

    assert chunk_count == 3


def test_load_corpus_rejects_missing_content_path(tmp_path: Path) -> None:
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps([_source("missing.md")]), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="No existe el contenido Markdown"):
        load_corpus(manifest)


def test_load_corpus_rejects_non_markdown_content(tmp_path: Path) -> None:
    content = tmp_path / "source.txt"
    content.write_text("Contenido.", encoding="utf-8")
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps([_source("source.txt")]), encoding="utf-8")

    with pytest.raises(ValueError, match="debe ser un archivo .md"):
        load_corpus(manifest)


def test_load_corpus_rejects_empty_markdown(tmp_path: Path) -> None:
    content = tmp_path / "source.md"
    content.write_text("   ", encoding="utf-8")
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps([_source("source.md")]), encoding="utf-8")

    with pytest.raises(ValueError, match="esta vacio"):
        load_corpus(manifest)
