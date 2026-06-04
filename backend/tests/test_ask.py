from fastapi.testclient import TestClient

from app.main import create_app


def test_ask_returns_cited_local_rag_response() -> None:
    client = TestClient(create_app())

    response = client.post("/ask", json={"question": "registro de jornada"})

    assert response.status_code == 200
    payload = response.json()
    assert "Respuesta basada en el corpus local disponible." in payload["answer"]
    assert payload["sources"]
    assert payload["sources"][0]["title"]
    assert payload["sources"][0]["url"]
    assert payload["sources"][0]["reference"]
    assert "No debe usarse como asesoramiento legal." in payload["limitations"]


def test_query_alias_returns_same_response_shape() -> None:
    client = TestClient(create_app())

    response = client.post("/query", json={"question": "Estatuto de los Trabajadores"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"answer", "sources", "limitations"}
    assert isinstance(payload["sources"], list)


def test_ask_rejects_blank_question() -> None:
    client = TestClient(create_app())

    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 422
