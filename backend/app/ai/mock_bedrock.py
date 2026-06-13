import re
from typing import Any


CITATION_PATTERN = re.compile(r"\[(\d+)\]")
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
        citations = sorted(set(CITATION_PATTERN.findall(prompt)), key=int)
        citation_text = f" [{citations[0]}]" if citations else ""
        question_text = question or "la consulta planteada"
        return (
            "Respuesta mock local: revisa la situacion concreta, conserva la documentacion "
            f"relevante y contrasta los plazos antes de actuar. Para {question_text}, la "
            f"orientacion debe tomarse como inicial y no como asesoramiento legal definitivo."
            f"{citation_text}"
        )

    def _extract_section(self, prompt: str, heading: str) -> str:
        if heading not in prompt:
            return ""
        section = prompt.split(heading, 1)[1].strip()
        return section.split("\n\n", 1)[0].strip()

    def _count_tokens(self, text: str) -> int:
        return len(WORD_PATTERN.findall(text))
