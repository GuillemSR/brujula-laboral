from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.routes import get_temporary_storage
from app.main import create_app
from app.storage.s3_temporary import StoredTemporaryDocument


class FakeTemporaryStorage:
    def __init__(self) -> None:
        self.saved: list[dict[str, object]] = []
        self.deleted: list[str] = []

    def put_document(
        self,
        *,
        document_id: str,
        content: bytes,
        content_type: str,
    ) -> StoredTemporaryDocument:
        self.saved.append(
            {
                "document_id": document_id,
                "content": content,
                "content_type": content_type,
            }
        )
        return StoredTemporaryDocument(
            document_id=document_id,
            key=f"temporary-documents/{document_id}",
            content_type=content_type,
            size_bytes=len(content),
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )

    def delete_document(self, document_id: str) -> None:
        self.deleted.append(document_id)


def build_client(storage: FakeTemporaryStorage) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_temporary_storage] = lambda: storage
    return TestClient(app)


def test_upload_document_stores_file_and_returns_temporary_document_id() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)

    response = client.post(
        "/documents",
        files={"file": ("contrato privado.txt", b"contenido privado", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "document_id",
        "filename",
        "content_type",
        "size_bytes",
        "expires_in_minutes",
    }
    assert payload["document_id"]
    assert payload["filename"] == "contrato_privado.txt"
    assert payload["content_type"] == "text/plain"
    assert payload["size_bytes"] == len(b"contenido privado")
    assert payload["expires_in_minutes"] == 30
    assert "contenido privado" not in response.text

    assert len(storage.saved) == 1
    saved = storage.saved[0]
    assert saved["document_id"] == payload["document_id"]
    assert saved["content"] == b"contenido privado"


def test_upload_document_rejects_empty_file() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)

    response = client.post(
        "/documents",
        files={"file": ("contrato.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert storage.saved == []


def test_upload_document_rejects_unsupported_extension() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)

    response = client.post(
        "/documents",
        files={"file": ("contrato.exe", b"contenido", "application/octet-stream")},
    )

    assert response.status_code == 415
    assert storage.saved == []


def test_upload_document_rejects_mismatched_content_type() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)

    response = client.post(
        "/documents",
        files={"file": ("contrato.pdf", b"contenido", "text/plain")},
    )

    assert response.status_code == 415
    assert storage.saved == []


def test_upload_document_rejects_oversized_file() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)
    oversized_content = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/documents",
        files={"file": ("contrato.txt", oversized_content, "text/plain")},
    )

    assert response.status_code == 413
    assert storage.saved == []


def test_delete_document_deletes_temporary_object() -> None:
    storage = FakeTemporaryStorage()
    client = build_client(storage)
    document_id = uuid4().hex

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert storage.deleted == [document_id]
