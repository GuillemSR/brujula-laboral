import re
from typing import Any


CITATION_PATTERN = re.compile(r"^\[(\d+)\]", re.MULTILINE)
WORD_PATTERN = re.compile(r"\S+")


class MockBedrockRuntimeClient:
    """Local stand-in for the Bedrock Runtime Converse API."""

    def converse(self, **kwargs: Any) -> dict[str, Any]:
        prompt = self._prompt_from_messages(kwargs.get("messages", []))
        text = self._answer(prompt)
        input_tokens = self._count_tokens(prompt)
        output_tokens = self._count_tokens(text)
        return {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": text}],
                }
            },
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": input_tokens,
                "outputTokens": output_tokens,
                "totalTokens": input_tokens + output_tokens,
            },
            "metrics": {
                "latencyMs": 1,
            },
        }

    def _prompt_from_messages(self, messages: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for message in messages:
            for block in message.get("content", []):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)

    def _answer(self, prompt: str) -> str:
        question = self._extract_section(prompt, "Consulta de la persona usuaria:")
        citations = self._citation_markers(prompt)
        question_text = self._short_text(question or "la consulta planteada")
        cited_note = (
            f" La referencia recuperada queda integrada en el texto como {citations[0]}."
            if citations
            else ""
        )
        cited_action = (
            f"Contrasta el fragmento citado {citations[0]} con la situacion concreta."
            if citations
            else "Contrasta la situacion concreta con una fuente oficial o asesoramiento laboral."
        )
        document_note = (
            "\n\nDocumento temporal: se ha tenido en cuenta como contexto de trabajo, sin "
            "reproducir su contenido privado."
            if "Contexto temporal de documento privado" in prompt
            else ""
        )
        return (
            "Respuesta mock local:\n\n"
            f"Resumen: para {question_text}, separaria tres planos: que ha ocurrido, "
            "que norma o convenio puede aplicar y que pruebas hay disponibles."
            f"{cited_note}\n\n"
            "Orientacion inicial:\n"
            "- Conserva contrato, nominas, comunicaciones y cualquier notificacion recibida.\n"
            "- Revisa si existe convenio colectivo aplicable antes de cerrar una conclusion.\n"
            "- Si hay plazos de reclamacion, no esperes a tener toda la documentacion perfecta.\n\n"
            "Matices importantes: esta respuesta sirve para probar una contestacion mas larga "
            "en la interfaz. Debe leerse como orientacion inicial, no como asesoramiento legal "
            "definitivo.\n\n"
            f"Siguiente paso: {cited_action}"
            f"{document_note}"
        )

    def _citation_markers(self, prompt: str) -> list[str]:
        citations = sorted(set(CITATION_PATTERN.findall(prompt)), key=int)
        return [f"[{citation}]" for citation in citations]

    def _extract_section(self, prompt: str, heading: str) -> str:
        if heading not in prompt:
            return ""
        section = prompt.split(heading, 1)[1].strip()
        return section.split("\n\n", 1)[0].strip()

    def _short_text(self, text: str, max_length: int = 180) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= max_length:
            return normalized
        return f"{normalized[: max_length - 1].rstrip()}..."

    def _count_tokens(self, text: str) -> int:
        return len(WORD_PATTERN.findall(text))
