from fastapi.testclient import TestClient

from app.main import create_app


def test_ask_returns_no_document_prototype_response() -> None:
    client = TestClient(create_app())

    response = client.post("/ask", json={"question": "¿Puedo negarme a hacer horas extra?"})

    assert response.status_code == 200
    payload = response.json()
    assert "Consulta recibida: ¿Puedo negarme a hacer horas extra?" in payload["answer"]
    assert payload["sources"] == []
    assert "Sin documento privado adjunto." in payload["limitations"]
    assert "Sin recuperacion RAG conectada todavia." in payload["limitations"]


def test_query_alias_returns_same_response_shape() -> None:
    client = TestClient(create_app())

    response = client.post("/query", json={"question": "¿Qué es un convenio colectivo?"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"answer", "sources", "limitations"}
    assert payload["sources"] == []


def test_ask_rejects_blank_question() -> None:
    client = TestClient(create_app())

    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 422
