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


def test_static_assets_are_served() -> None:
    client = TestClient(create_app())

    script_response = client.get("/static/app.js")
    styles_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert 'fetch("/ask"' in script_response.text
    assert "Fuentes consultadas" in script_response.text
    assert "limitations-section" not in script_response.text
    assert styles_response.status_code == 200
    assert "text/css" in styles_response.headers["content-type"]
    assert ".privacy-notice" in styles_response.text
    assert ".limitations-section" not in styles_response.text
