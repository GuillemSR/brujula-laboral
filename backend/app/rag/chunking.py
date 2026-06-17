import re
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


SECTION_PATTERN = re.compile(
    r"^(?P<section>(?:#{1,6}\s+.+)|(?:Articulo\s+\d+[^\n]*)|(?:Clausula\s+\d+[^\n]*))$",
    re.IGNORECASE,
)
MAX_SECTION_LABEL_LENGTH = 200
MAX_CITATION_LABEL_LENGTH = 500


def _truncate_label(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3].rstrip()}..."


def _normalize_section(line: str) -> str:
    section = line.strip().lstrip("#").strip()
    return re.sub(r"\s+", " ", section)


def _split_legal_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "documento-completo"
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if SECTION_PATTERN.match(stripped):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = _normalize_section(stripped)
            current_lines = [stripped]
            continue

        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    return [
        (section, "\n".join(lines).strip())
        for section, lines in sections
        if "\n".join(lines).strip()
    ]


def chunk_document(document: SourceDocument) -> list[Chunk]:
    """Split legal Markdown-like sources by headings, articles or clauses."""
    text = document.text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    for index, (section, section_text) in enumerate(_split_legal_sections(text)):
        chunk_id = f"{document.source_id}:{index}"
        section_label = _truncate_label(section, MAX_SECTION_LABEL_LENGTH)
        citation_label = _truncate_label(
            f"{document.title}, {section_label}", MAX_CITATION_LABEL_LENGTH
        )
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                source_id=document.source_id,
                text=section_text,
                section=section_label,
                citation_label=citation_label,
                metadata=document.metadata.to_chunk_metadata(
                    chunk_id=chunk_id,
                    section=section_label,
                    citation_label=citation_label,
                ),
            )
        )

    return chunks
