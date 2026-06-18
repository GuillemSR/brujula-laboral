from fastapi.testclient import TestClient

import json

import app.api.routes as routes
from app.api.routes import (
    get_answer_generator,
    get_streaming_answer_generator,
    get_temporary_storage_factory,
)
from app.ai.bedrock_client import ModelResponse
from app.core.config import Settings
from app.main import create_app
from app.storage.s3_temporary import RetrievedTemporaryDocument


class FakeTemporaryStorage:
    def __init__(
        self,
        documents: dict[str, RetrievedTemporaryDocument] | None = None,
        missing_document_ids: set[str] | None = None,
    ) -> None:
        self.documents = documents or {}
        self.missing_document_ids = missing_document_ids or set()

    def get_document(self, document_id: str) -> RetrievedTemporaryDocument:
        if document_id in self.missing_document_ids:
            raise ValueError("Temporary document not found")
        return self.documents[document_id]


def build_client(storage: FakeTemporaryStorage | None = None) -> TestClient:
    app = create_app()
    temporary_storage = storage or FakeTemporaryStorage()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: temporary_storage
    app.dependency_overrides[get_answer_generator] = lambda: None
    return TestClient(app)


def test_ask_returns_cited_local_rag_response() -> None:
    client = build_client()

    response = client.post("/ask", json={"question": "registro de jornada"})

    assert response.status_code == 200
    payload = response.json()
    assert "referencias principales" in payload["answer"]
    assert payload["sources"]
    assert payload["sources"][0]["title"]
    assert payload["sources"][0]["url"]
    assert payload["sources"][0]["reference"]
    assert "No debe usarse como asesoramiento legal." in payload["limitations"]


def test_ask_without_relevant_public_sources_still_answers() -> None:
    client = build_client()

    response = client.post("/ask", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    payload = response.json()
    assert "orientacion general" in payload["answer"]
    assert payload["sources"] == []
    assert "registro de jornada" not in response.text.lower()


def test_ask_uses_model_generator_when_available() -> None:
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    app.dependency_overrides[get_answer_generator] = lambda: (
        lambda _prompt, _system_prompt: ModelResponse(
            text="Respuesta generada por modelo.",
            model_id="test",
        )
    )
    client = TestClient(app)

    response = client.post("/ask", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Respuesta generada por modelo."
    assert payload["sources"] == []


def test_ask_stream_returns_meta_and_chunks() -> None:
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    app.dependency_overrides[get_streaming_answer_generator] = lambda: (
        lambda _prompt, _system_prompt: iter(["Respuesta ", "streaming."])
    )
    client = TestClient(app)

    response = client.post("/ask/stream", json={"question": "registro de jornada"})

    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers["content-type"]
    events = [json.loads(line) for line in response.text.splitlines()]
    assert events[0]["type"] == "meta"
    assert events[0]["sources"]
    assert events[1] == {"type": "chunk", "text": "Respuesta "}
    assert events[2] == {"type": "chunk", "text": "streaming."}
    assert events[-1] == {"type": "done"}


def test_ask_stream_falls_back_to_local_answer_without_stream_generator() -> None:
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    app.dependency_overrides[get_streaming_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post("/ask/stream", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines()]
    assert events[0] == {
        "type": "meta",
        "sources": [],
        "limitations": [
            "Respuesta orientativa.",
            "Las fuentes del corpus se muestran solo cuando hay coincidencias relevantes.",
            "No debe usarse como asesoramiento legal.",
        ],
    }
    assert events[1]["type"] == "chunk"
    assert "orientacion general" in events[1]["text"]
    assert events[-1] == {"type": "done"}


def test_ask_uses_mock_provider_when_configured(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: Settings(ai_provider="mock", bedrock_model_id=None),
    )
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "registro de jornada"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("Respuesta mock local:")
    assert "Orientacion inicial:" in payload["answer"]
    assert "Siguiente paso:" in payload["answer"]
    assert "[1]" in payload["answer"]
    assert payload["sources"]


def test_ask_mock_provider_without_sources_does_not_add_fake_citation(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: Settings(ai_provider="mock", bedrock_model_id=None),
    )
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("Respuesta mock local:")
    assert "[1]" not in payload["answer"]
    assert payload["sources"] == []


def test_ask_uses_ollama_provider_when_configured(monkeypatch) -> None:
    class FakeOllamaClient:
        def __init__(self, settings: Settings) -> None:
            self.settings = settings

        def generate(self, _prompt: str, _system_prompt: str) -> ModelResponse:
            return ModelResponse(
                text="Respuesta desde Ollama.", model_id=self.settings.ollama_model_id
            )

    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: Settings(ai_provider="ollama", ollama_model_id="qwen2.5:1.5b"),
    )
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)

    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Respuesta desde Ollama."
    assert payload["sources"] == []


def test_bedrock_provider_without_model_id_uses_local_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: Settings(ai_provider="bedrock", bedrock_model_id=None),
    )
    app = create_app()
    app.dependency_overrides[get_temporary_storage_factory] = lambda: lambda: FakeTemporaryStorage()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "criptomonedas saturno"})

    assert response.status_code == 200
    payload = response.json()
    assert "orientacion general" in payload["answer"]
    assert payload["sources"] == []


def test_query_alias_returns_same_response_shape() -> None:
    client = build_client()

    response = client.post("/query", json={"question": "Estatuto de los Trabajadores"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"answer", "sources", "limitations"}
    assert isinstance(payload["sources"], list)


def test_ask_rejects_blank_question() -> None:
    client = build_client()

    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 422


def test_ask_with_document_extracts_text_without_echoing_private_content() -> None:
    document_id = "a" * 32
    private_text = "registro de jornada contenido privado de mi contrato"
    storage = FakeTemporaryStorage(
        documents={
            document_id: RetrievedTemporaryDocument(
                document_id=document_id,
                content=private_text.encode(),
                content_type="text/plain",
                size_bytes=len(private_text),
            )
        }
    )
    client = build_client(storage)

    response = client.post(
        "/ask",
        json={"question": "Que derechos tengo?", "document_id": document_id},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "referencias principales" in payload["answer"]
    assert "contenido privado" not in response.text
    assert any(
        "Documento privado temporal extraido solo en memoria" in limitation
        for limitation in payload["limitations"]
    )


def test_ask_with_missing_document_returns_privacy_safe_error() -> None:
    document_id = "b" * 32
    storage = FakeTemporaryStorage(missing_document_ids={document_id})
    client = build_client(storage)

    response = client.post(
        "/ask",
        json={"question": "Que derechos tengo?", "document_id": document_id},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Documento temporal no encontrado o expirado. Vuelve a subirlo."
    }


def test_ask_with_unsupported_document_format_returns_privacy_safe_error() -> None:
    document_id = "c" * 32
    private_text = "contenido privado del documento"
    storage = FakeTemporaryStorage(
        documents={
            document_id: RetrievedTemporaryDocument(
                document_id=document_id,
                content=private_text.encode(),
                content_type="application/pdf",
                size_bytes=len(private_text),
            )
        }
    )
    client = build_client(storage)

    response = client.post(
        "/ask",
        json={"question": "Que derechos tengo?", "document_id": document_id},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "El formato del documento todavia no permite extraer texto."
    }
    assert "contenido privado" not in response.text
