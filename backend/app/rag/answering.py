from dataclasses import dataclass

from app.rag.citations import format_citation_list
from app.rag.retrieval import RetrievalResult


@dataclass(frozen=True)
class CitedSource:
    title: str
    url: str | None
    reference: str | None


@dataclass(frozen=True)
class CitedAnswer:
    answer: str
    sources: list[CitedSource]
    limitations: list[str]


def _snippet(text: str, max_length: int = 360) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 1].rstrip()}..."


def build_cited_answer(question: str, results: list[RetrievalResult]) -> CitedAnswer:
    if not results:
        return CitedAnswer(
            answer=(
                "No he encontrado fuentes del corpus local suficientemente relevantes para "
                f"responder a esta consulta: {question}"
            ),
            sources=[],
            limitations=[
                "Corpus local limitado.",
                "Sin modelo generativo externo conectado.",
                "No debe usarse como asesoramiento legal.",
            ],
        )

    citation_labels = format_citation_list(results)
    evidence_lines = [
        f"{label}: {_snippet(result.chunk.text)}" for label, result in zip(citation_labels, results)
    ]
    answer = (
        "Respuesta basada en el corpus local disponible. "
        "Revisa las fuentes citadas antes de tomar una decision laboral o sindical.\n\n"
        + "\n\n".join(evidence_lines)
    )
    sources = [
        CitedSource(
            title=result.chunk.metadata.source.title,
            url=result.chunk.metadata.source.source_url.unicode_string(),
            reference=result.chunk.citation_label,
        )
        for result in results
    ]
    return CitedAnswer(
        answer=answer,
        sources=sources,
        limitations=[
            "Respuesta extractiva de prototipo, sin razonamiento juridico completo.",
            "Corpus local limitado y pendiente de ampliacion.",
            "No debe usarse como asesoramiento legal.",
        ],
    )
