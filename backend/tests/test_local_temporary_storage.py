from app.core.config import Settings
from app.storage.local import InMemoryTemporaryDocumentStorage


def test_in_memory_temporary_storage_stores_reads_and_deletes_document() -> None:
    storage = InMemoryTemporaryDocumentStorage(settings=Settings(temp_document_ttl_minutes=30))
    document_id = "a" * 32

    stored = storage.put_document(
        document_id=document_id,
        content=b"contenido temporal",
        content_type="text/plain",
    )
    retrieved = storage.get_document(document_id)

    assert stored.document_id == document_id
    assert stored.key == f"memory://temporary-documents/{document_id}"
    assert retrieved.content == b"contenido temporal"
    assert retrieved.content_type == "text/plain"

    storage.delete_document(document_id)

    try:
        storage.get_document(document_id)
    except ValueError as exc:
        assert str(exc) == "Temporary document not found"
    else:
        raise AssertionError("Expected deleted document to be unavailable")


def test_in_memory_temporary_storage_rejects_invalid_document_id() -> None:
    storage = InMemoryTemporaryDocumentStorage()

    try:
        storage.put_document(
            document_id="../contrato",
            content=b"contenido",
            content_type="text/plain",
        )
    except ValueError as exc:
        assert str(exc) == "Invalid temporary document id"
    else:
        raise AssertionError("Expected invalid document id to be rejected")
