from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    text: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    text: str
    metadata: dict[str, str]


def chunk_document(document: SourceDocument) -> list[Chunk]:
    """Initial placeholder chunker.

    The real implementation should split legal sources by article, clause or section.
    """
    text = document.text.strip()
    if not text:
        return []

    return [
        Chunk(
            chunk_id=f"{document.source_id}:0",
            source_id=document.source_id,
            text=text,
            metadata=document.metadata,
        )
    ]
