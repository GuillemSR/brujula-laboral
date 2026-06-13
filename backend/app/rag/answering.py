from dataclasses import dataclass
from re import findall
from typing import Callable

from app.ai.bedrock_client import ModelResponse
from app.rag.citations import format_citation_list
from app.rag.retrieval import RetrievalResult

MIN_QUERY_TOKEN_OVERLAP = 1
STOPWORDS = {
    "ante",
    "cada",
    "como",
    "con",
    "cual",
    "cuando",
    "del",
    "desde",
    "donde",
    "el",
    "ella",
    "ellos",
    "en",
    "entre",
    "esa",
    "ese",
    "eso",
    "esta",
    "este",
    "esto",
    "hay",
    "las",
    "los",
    "mas",
    "me",
    "mis",
    "para",
    "pero",
    "por",
    "pueden",
    "que",
    "sin",
    "sobre",
    "sus",
    "tengo",
    "una",
    "uno",
}


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


GenerateAnswer = Callable[[str, str], ModelResponse]
SYSTEM_PROMPT = (
    "Eres Brujula Laboral, un asistente laboral y sindical para Espana. "
    "Responde en espanol claro, con tono prudente y util. No digas que no puedes "
    "responder solo porque no haya fuentes del corpus. Si hay fuentes RAG, usalas "
    "como referencia principal y cita sus marcadores, por ejemplo [1]. Si no hay "
    "fuentes RAG, responde igualmente con orientacion general sin mencionar esa "
    "ausencia al usuario, y recomienda revisar el caso concreto con una persona "
    "profesional, sindicato o fuente oficial. No "
    "inventes articulos, sentencias ni fuentes. No presentes la respuesta como "
    "asesoramiento legal definitivo."
)


def _snippet(text: str, max_length: int = 360) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 1].rstrip()}..."


def _tokens(text: str) -> set[str]:
    return {
        token for token in findall(r"[a-záéíóúüñ0-9]{4,}", text.lower()) if token not in STOPWORDS
    }


def _matches_query_terms(question: str, result: RetrievalResult) -> bool:
    query_tokens = _tokens(question)
    if not query_tokens:
        return True

    source = result.chunk.metadata.source
    searchable_text = " ".join(
        [
            result.chunk.text,
            result.chunk.section or "",
            source.title,
            source.publisher,
            source.sector,
            source.territory,
        ]
    )
    return len(query_tokens & _tokens(searchable_text)) >= MIN_QUERY_TOKEN_OVERLAP


def _sources(results: list[RetrievalResult]) -> list[CitedSource]:
    return [
        CitedSource(
            title=result.chunk.metadata.source.title,
            url=result.chunk.metadata.source.source_url.unicode_string(),
            reference=result.chunk.citation_label,
        )
        for result in results
    ]


def _evidence_block(results: list[RetrievalResult]) -> str:
    if not results:
        return "Sin fragmentos de apoyo para citar. No menciones esta linea al usuario."

    citation_labels = format_citation_list(results)
    evidence_lines = [
        f"{label}: {_snippet(result.chunk.text)}" for label, result in zip(citation_labels, results)
    ]
    return "\n\n".join(evidence_lines)


def build_answer_prompt(
    question: str,
    results: list[RetrievalResult],
    private_context: str | None = None,
) -> str:
    private_context_block = (
        "Contexto temporal de documento privado aportado por la persona usuaria:\n"
        f"{_snippet(private_context, 1800)}\n\n"
        if private_context
        else ""
    )
    return (
        "Consulta de la persona usuaria:\n"
        f"{question}\n\n"
        f"{private_context_block}"
        "Fuentes RAG disponibles:\n"
        f"{_evidence_block(results)}\n\n"
        "Instrucciones de formato:\n"
        "- Da una respuesta unica y directa.\n"
        "- Si usas una fuente RAG, cita el marcador correspondiente como [1].\n"
        "- Si no hay fuentes RAG, no menciones esa ausencia al usuario.\n"
        "- Incluye matices, riesgos y siguientes pasos practicos cuando proceda.\n"
    )


def _fallback_answer(question: str, results: list[RetrievalResult]) -> str:
    if results:
        return (
            "Con la informacion disponible, estas son las referencias principales que conviene "
            "revisar antes de tomar una decision:\n\n"
            f"{_evidence_block(results)}\n\n"
            "Contrasta el caso concreto con una fuente oficial, un sindicato o una persona "
            "profesional antes de actuar."
        )

    return (
        "Como orientacion general, revisa primero cual es el hecho laboral concreto, que "
        "documentacion existe y que plazo puede aplicar. Si hay una decision empresarial, "
        "conviene conservar comunicaciones, contrato, nominas y cualquier notificacion, y "
        "consultar cuanto antes con un sindicato, graduado social o abogado laboralista.\n\n"
        "La respuesta debe tomarse como orientacion inicial, no como una valoracion legal "
        "definitiva del caso."
    )


def build_cited_answer(
    question: str,
    results: list[RetrievalResult],
    relevance_query: str | None = None,
    private_context: str | None = None,
    generate_answer: GenerateAnswer | None = None,
) -> CitedAnswer:
    results = [
        result for result in results if _matches_query_terms(relevance_query or question, result)
    ]
    prompt = build_answer_prompt(
        question=question,
        results=results,
        private_context=private_context,
    )
    if generate_answer:
        try:
            answer = generate_answer(prompt, SYSTEM_PROMPT).text.strip()
            if not answer:
                answer = _fallback_answer(question, results)
        except RuntimeError:
            answer = _fallback_answer(question, results)
    else:
        answer = _fallback_answer(question, results)

    return CitedAnswer(
        answer=answer,
        sources=_sources(results),
        limitations=[
            "Respuesta orientativa.",
            "Las fuentes del corpus se muestran solo cuando hay coincidencias relevantes.",
            "No debe usarse como asesoramiento legal.",
        ],
    )
