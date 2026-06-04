from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.rag.chunking import SourceDocument
from app.rag.metadata import RagSourceMetadata, load_source_manifest


@dataclass(frozen=True)
class LoadedCorpus:
    manifest_path: Path
    documents: list[SourceDocument]


def load_markdown_source(source: RagSourceMetadata, manifest_dir: Path) -> SourceDocument:
    if source.content_path is None:
        raise ValueError(f"{source.source_id} no tiene content_path configurado.")

    content_path = (manifest_dir / source.content_path).resolve()
    if not content_path.is_file():
        raise FileNotFoundError(
            f"No existe el contenido Markdown de {source.source_id}: {content_path}"
        )

    if content_path.suffix.lower() != ".md":
        raise ValueError(f"El contenido de {source.source_id} debe ser un archivo .md.")

    text = content_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"El contenido Markdown de {source.source_id} esta vacio.")

    return SourceDocument(
        source_id=source.source_id,
        title=source.title,
        text=text,
        metadata=source,
    )


def load_corpus(manifest_path: Path) -> LoadedCorpus:
    resolved_manifest = manifest_path.resolve()
    sources = load_source_manifest(resolved_manifest)
    documents = [
        load_markdown_source(source=source, manifest_dir=resolved_manifest.parent)
        for source in sources
    ]
    return LoadedCorpus(manifest_path=resolved_manifest, documents=documents)
