from dataclasses import dataclass

from app.rag.metadata import RagChunkMetadata, RagSourceMetadata


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    text: str
    metadata: RagSourceMetadata


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    text: str
    section: str
    citation_label: str
    metadata: RagChunkMetadata


def chunk_document(document: SourceDocument) -> list[Chunk]:
    """Initial placeholder chunker.

    The real implementation should split legal sources by article, clause or section.
    """
    text = document.text.strip()
    if not text:
        return []

    chunk_id = f"{document.source_id}:0"
    section = "documento-completo"
    citation_label = f"{document.title}, documento completo"

    return [
        Chunk(
            chunk_id=chunk_id,
            source_id=document.source_id,
            text=text,
            section=section,
            citation_label=citation_label,
            metadata=document.metadata.to_chunk_metadata(
                chunk_id=chunk_id,
                section=section,
                citation_label=citation_label,
            ),
        )
    ]
