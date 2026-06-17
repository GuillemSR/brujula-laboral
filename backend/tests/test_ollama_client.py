import json

import pytest

from app.ai.ollama_client import OllamaClient
from app.core.config import Settings


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, object] | None = None,
        lines: list[dict[str, object]] | None = None,
    ) -> None:
        self.payload = payload
        self.lines = lines or []

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __iter__(self):
        return iter([f"{json.dumps(line)}\n".encode("utf-8") for line in self.lines])


def test_ollama_client_calls_generate_api() -> None:
    calls = []

    def open_url(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(
            {
                "response": "Respuesta generada por Ollama.",
                "model": "qwen2.5:1.5b",
                "prompt_eval_count": 12,
                "eval_count": 8,
            }
        )

    settings = Settings(
        ai_provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model_id="qwen2.5:1.5b",
        ollama_timeout_seconds=30,
    )
    client = OllamaClient(settings=settings, open_url=open_url)

    response = client.generate("Pregunta", "Sistema", max_tokens=300, temperature=0.1)

    request, timeout = calls[0]
    payload = json.loads(request.data.decode("utf-8"))
    assert request.full_url == "http://127.0.0.1:11434/api/generate"
    assert timeout == 30
    assert payload["model"] == "qwen2.5:1.5b"
    assert payload["prompt"] == "Pregunta"
    assert payload["system"] == "Sistema"
    assert payload["stream"] is False
    assert payload["options"] == {"num_predict": 300, "temperature": 0.1}
    assert response.text == "Respuesta generada por Ollama."
    assert response.model_id == "qwen2.5:1.5b"
    assert response.input_tokens == 12
    assert response.output_tokens == 8


def test_ollama_client_streams_generate_chunks() -> None:
    calls = []

    def open_url(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(
            lines=[
                {"response": "Primera ", "done": False},
                {"response": "parte", "done": False},
                {"response": "", "done": True},
            ]
        )

    settings = Settings(
        ai_provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model_id="qwen2.5:1.5b",
    )
    client = OllamaClient(settings=settings, open_url=open_url)

    chunks = list(client.stream("Pregunta", "Sistema", max_tokens=120, temperature=0.3))

    request, timeout = calls[0]
    payload = json.loads(request.data.decode("utf-8"))
    assert request.full_url == "http://127.0.0.1:11434/api/generate"
    assert timeout == 120.0
    assert payload["stream"] is True
    assert payload["options"] == {"num_predict": 120, "temperature": 0.3}
    assert chunks == ["Primera ", "parte"]


def test_ollama_client_errors_are_runtime_errors() -> None:
    def open_url(_request, timeout):
        assert timeout == 120.0
        raise OSError("connection refused")

    client = OllamaClient(settings=Settings(ai_provider="ollama"), open_url=open_url)

    with pytest.raises(RuntimeError, match="Ollama"):
        client.generate("Pregunta", "Sistema")
