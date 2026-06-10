from io import BytesIO

from app.core.config import Settings
from app.storage.s3_temporary import S3TemporaryStorage


class FakeS3Client:
    def __init__(self) -> None:
        self.put_kwargs: dict[str, object] | None = None
        self.deleted: list[dict[str, str]] = []
        self.get_object_response: dict[str, object] | None = None

    def put_object(self, **kwargs: object) -> None:
        self.put_kwargs = kwargs

    def delete_object(self, **kwargs: str) -> None:
        self.deleted.append(kwargs)

    def get_object(self, **kwargs: str) -> dict[str, object]:
        if self.get_object_response is None:
            raise AssertionError(f"Unexpected get_object call: {kwargs}")
        return self.get_object_response


def test_put_document_uses_internal_key_encryption_and_non_sensitive_metadata() -> None:
    client = FakeS3Client()
    storage = S3TemporaryStorage(
        client=client,
        settings=Settings(
            s3_temp_bucket="bucket-temporal",
            temp_document_ttl_minutes=30,
            kms_key_id=None,
        ),
    )

    document_id = "a" * 32

    stored = storage.put_document(
        document_id=document_id,
        content=b"contenido privado",
        content_type="text/plain",
    )

    assert stored.key == f"temporary-documents/{document_id}"
    assert client.put_kwargs is not None
    assert client.put_kwargs["Bucket"] == "bucket-temporal"
    assert client.put_kwargs["Key"] == f"temporary-documents/{document_id}"
    assert client.put_kwargs["ServerSideEncryption"] == "AES256"
    assert client.put_kwargs["ContentType"] == "text/plain"
    metadata = client.put_kwargs["Metadata"]
    assert metadata == {
        "document-id": document_id,
        "expires-at": stored.expires_at.isoformat(),
    }
    assert "contenido privado" not in str(metadata)
    assert "contrato" not in str(client.put_kwargs["Key"])


def test_delete_document_uses_internal_key() -> None:
    client = FakeS3Client()
    storage = S3TemporaryStorage(
        client=client,
        settings=Settings(s3_temp_bucket="bucket-temporal"),
    )

    document_id = "b" * 32

    storage.delete_document(document_id)

    assert client.deleted == [
        {"Bucket": "bucket-temporal", "Key": f"temporary-documents/{document_id}"}
    ]


def test_get_document_reads_temporary_object_without_sensitive_metadata() -> None:
    client = FakeS3Client()
    client.get_object_response = {
        "Body": BytesIO(b"contenido privado"),
        "ContentType": "text/plain",
    }
    storage = S3TemporaryStorage(
        client=client,
        settings=Settings(s3_temp_bucket="bucket-temporal"),
    )

    document_id = "c" * 32

    retrieved = storage.get_document(document_id)

    assert retrieved.document_id == document_id
    assert retrieved.content == b"contenido privado"
    assert retrieved.content_type == "text/plain"
    assert retrieved.size_bytes == len(b"contenido privado")


def test_build_key_rejects_invalid_document_id() -> None:
    storage = S3TemporaryStorage(
        client=FakeS3Client(),
        settings=Settings(s3_temp_bucket="bucket-temporal"),
    )

    try:
        storage.build_key("../contrato")
    except ValueError as exc:
        assert str(exc) == "Invalid temporary document id"
    else:
        raise AssertionError("Expected invalid document id to be rejected")
