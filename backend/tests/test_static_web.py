from fastapi.testclient import TestClient

from app.main import create_app


def test_index_serves_static_web() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Brujula Laboral" in response.text
    assert "/static/app.js" in response.text
    assert "/static/styles.css" in response.text
    assert "Placeholder temporal" in response.text
    assert "Adjuntar documento temporal" in response.text
    assert "no se guarda por defecto" in response.text
    assert "privacy-confirmation" not in response.text
    assert 'id="result" class="box result" aria-live="polite" aria-label="Resultado" hidden' in (
        response.text
    )


def test_static_assets_are_served() -> None:
    client = TestClient(create_app())

    script_response = client.get("/static/app.js")
    styles_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert 'fetch("/ask/stream"' in script_response.text
    assert "readStreamingAnswer" in script_response.text
    assert "Fuentes consultadas" in script_response.text
    assert "Limites de la respuesta" not in script_response.text
    assert "privacyConfirmation" not in script_response.text
    assert "question-count" in script_response.text
    assert styles_response.status_code == 200
    assert "text/css" in styles_response.headers["content-type"]
    assert "[hidden]" in styles_response.text
    assert "display: none !important" in styles_response.text
    assert "hero-waves.png" not in styles_response.text
    assert ".box" in styles_response.text
