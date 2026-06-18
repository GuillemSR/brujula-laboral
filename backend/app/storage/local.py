from datetime import UTC, datetime, timedelta
from pathlib import Path
from re import fullmatch
from threading import Lock

from app.core.config import Settings, get_settings
from app.storage.s3_temporary import RetrievedTemporaryDocument, StoredTemporaryDocument


class LocalTemporaryStorage:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path

    def ensure(self) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)


class InMemoryTemporaryDocumentStorage:
    """Ephemeral local document store for development without S3."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._documents: dict[str, RetrievedTemporaryDocument] = {}
        self._expires_at: dict[str, datetime] = {}
        self._lock = Lock()

    def put_document(
        self,
        *,
        document_id: str,
        content: bytes,
        content_type: str,
    ) -> StoredTemporaryDocument:
        self._validate_document_id(document_id)
        expires_at = datetime.now(UTC) + timedelta(minutes=self.settings.temp_document_ttl_minutes)
        with self._lock:
            self._documents[document_id] = RetrievedTemporaryDocument(
                document_id=document_id,
                content=content,
                content_type=content_type,
                size_bytes=len(content),
            )
            self._expires_at[document_id] = expires_at

        return StoredTemporaryDocument(
            document_id=document_id,
            key=f"memory://temporary-documents/{document_id}",
            content_type=content_type,
            size_bytes=len(content),
            expires_at=expires_at,
        )

    def get_document(self, document_id: str) -> RetrievedTemporaryDocument:
        self._validate_document_id(document_id)
        with self._lock:
            self._delete_if_expired(document_id)
            document = self._documents.get(document_id)
            if document is None:
                raise ValueError("Temporary document not found")
            return document

    def delete_document(self, document_id: str) -> None:
        self._validate_document_id(document_id)
        with self._lock:
            self._documents.pop(document_id, None)
            self._expires_at.pop(document_id, None)

    def _delete_if_expired(self, document_id: str) -> None:
        expires_at = self._expires_at.get(document_id)
        if expires_at is not None and expires_at <= datetime.now(UTC):
            self._documents.pop(document_id, None)
            self._expires_at.pop(document_id, None)

    def _validate_document_id(self, document_id: str) -> None:
        if not fullmatch(r"[a-f0-9]{32}", document_id):
            raise ValueError("Invalid temporary document id")
