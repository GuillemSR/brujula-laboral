import logging
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

import app.api.routes as routes
from app.api.routes import (
    get_answer_generator,
    get_temporary_storage,
    get_temporary_storage_factory,
)
from app.main import VALIDATION_ERROR_DETAIL, create_app
from app.storage.s3_temporary import RetrievedTemporaryDocument, StoredTemporaryDocument


class FailingUploadStorage:
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def put_document(
        self,
        *,
        document_id: str,
        content: bytes,
        content_type: str,
    ) -> StoredTemporaryDocument:
        raise RuntimeError(self.error_message)


class FailingReadStorage:
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def get_document(self, document_id: str) -> RetrievedTemporaryDocument:
        raise RuntimeError(self.error_message)


class WorkingReadStorage:
    def __init__(self, document: RetrievedTemporaryDocument) -> None:
        self.document = document

    def get_document(self, document_id: str) -> RetrievedTemporaryDocument:
        return self.document


class WorkingUploadStorage:
    def __init__(self) -> None:
        self.saved: list[bytes] = []

    def put_document(
        self,
        *,
        document_id: str,
        content: bytes,
        content_type: str,
    ) -> StoredTemporaryDocument:
        self.saved.append(content)
        return StoredTemporaryDocument(
            document_id=document_id,
            key=f"temporary-documents/{document_id}",
            content_type=content_type,
            size_bytes=len(content),
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )


def test_validation_errors_do_not_echo_sensitive_inputs_or_log_them(caplog) -> None:
    caplog.set_level(logging.INFO)
    app = create_app()
    app.dependency_overrides[get_answer_generator] = lambda: None
    client = TestClient(app)
    sentinel = "SENTINELA_PRIVADA_NOMINA_123456789"

    response = client.post("/ask", json={"question": sentinel * 200})

    assert response.status_code == 422
    assert response.json() == {"detail": VALIDATION_ERROR_DETAIL}
    assert sentinel not in response.text
    assert sentinel not in caplog.text


def test_upload_storage_errors_do_not_echo_sensitive_content_or_log_it(caplog) -> None:
    caplog.set_level(logging.INFO)
    sentinel = "SENTINELA_PRIVADA_CONTRATO_987654321"
    app = create_app()
    app.dependency_overrides[get_temporary_storage] = lambda: FailingUploadStorage(
        f"fallo interno con {sentinel}"
    )
    client = TestClient(app)

    response = client.post(
        "/documents",
        files={"file": ("nomina-persona.txt", sentinel.encode(), "text/plain")},
    )

    assert response.status_code == 503
    assert sentinel not in response.text
    assert "nomina-persona" not in response.text
    assert sentinel not in caplog.text


def test_upload_storage_constructor_errors_are_privacy_safe(caplog, monkeypatch) -> None:
    caplog.set_level(logging.INFO)
    sentinel = "SENTINELA_CLIENTE_S3_444"

    class FailingStorageConstructor:
        def __init__(self) -> None:
            raise RuntimeError(f"fallo interno con {sentinel}")

    monkeypatch.setattr(routes, "S3TemporaryStorage", FailingStorageConstructor)
    client = TestClient(create_app())

    response = client.post(
        "/documents",
        files={"file": ("contrato-privado.txt", b"contenido privado", "text/plain")},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": routes.TEMPORARY_STORAGE_UNAVAILABLE_DETAIL}
    assert sentinel not in response.text
    assert sentinel not in caplog.text


def test_ask_storage_errors_do_not_echo_sensitive_question_or_log_it(caplog) -> None:
    caplog.set_level(logging.INFO)
    sentinel = "SENTINELA_PRIVADA_PREGUNTA_456789123"
    app = create_app()
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_temporary_storage_factory] = lambda: (
        lambda: FailingReadStorage(f"fallo interno con {sentinel}")
    )
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": f"Pregunta privada {sentinel}", "document_id": "a" * 32},
    )

    assert response.status_code == 503
    assert sentinel not in response.text
    assert sentinel not in caplog.text


def test_ask_storage_constructor_errors_are_privacy_safe(caplog, monkeypatch) -> None:
    caplog.set_level(logging.INFO)
    sentinel = "SENTINELA_CLIENTE_S3_555"

    class FailingStorageConstructor:
        def __init__(self) -> None:
            raise RuntimeError(f"fallo interno con {sentinel}")

    monkeypatch.setattr(routes, "S3TemporaryStorage", FailingStorageConstructor)
    app = create_app()
    app.dependency_overrides[get_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": f"Pregunta privada {sentinel}", "document_id": "a" * 32},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": routes.TEMPORARY_STORAGE_UNAVAILABLE_DETAIL}
    assert sentinel not in response.text
    assert sentinel not in caplog.text


def test_private_document_flow_does_not_log_question_or_extracted_text(caplog) -> None:
    caplog.set_level(logging.INFO)
    question_sentinel = "SENTINELA_PRIVADA_PREGUNTA_111"
    document_sentinel = "SENTINELA_PRIVADA_DOCUMENTO_222"
    document_id = "b" * 32
    document = RetrievedTemporaryDocument(
        document_id=document_id,
        content=f"registro de jornada {document_sentinel}".encode(),
        content_type="text/plain",
        size_bytes=len(document_sentinel),
    )
    app = create_app()
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_temporary_storage_factory] = lambda: (
        lambda: WorkingReadStorage(document)
    )
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": f"Que derechos tengo? {question_sentinel}", "document_id": document_id},
    )

    assert response.status_code == 200
    assert document_sentinel not in response.text
    assert question_sentinel not in caplog.text
    assert document_sentinel not in caplog.text


def test_private_upload_flow_does_not_log_file_content(caplog) -> None:
    caplog.set_level(logging.INFO)
    sentinel = "SENTINELA_PRIVADA_SUBIDA_333"
    storage = WorkingUploadStorage()
    app = create_app()
    app.dependency_overrides[get_temporary_storage] = lambda: storage
    client = TestClient(app)

    response = client.post(
        "/documents",
        files={"file": ("contrato-privado.txt", sentinel.encode(), "text/plain")},
    )

    assert response.status_code == 200
    assert sentinel not in response.text
    assert sentinel not in caplog.text
