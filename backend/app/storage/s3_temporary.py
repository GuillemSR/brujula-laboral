from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from re import fullmatch
from typing import Any

import boto3

from app.core.config import Settings, get_settings


TEMPORARY_DOCUMENT_PREFIX = "temporary-documents"


@dataclass(frozen=True)
class StoredTemporaryDocument:
    document_id: str
    key: str
    content_type: str
    size_bytes: int
    expires_at: datetime


class S3TemporaryStorage:
    def __init__(self, client: Any | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client or boto3.client("s3", region_name=self.settings.aws_region)

    def assert_configured(self) -> None:
        if not self.settings.s3_temp_bucket:
            raise RuntimeError("S3_TEMP_BUCKET is not configured")

    def put_document(
        self,
        *,
        document_id: str,
        content: bytes,
        content_type: str,
    ) -> StoredTemporaryDocument:
        self.assert_configured()
        key = self.build_key(document_id)
        expires_at = datetime.now(UTC) + timedelta(minutes=self.settings.temp_document_ttl_minutes)

        put_kwargs: dict[str, Any] = {
            "Bucket": self.settings.s3_temp_bucket,
            "Key": key,
            "Body": content,
            "ContentType": content_type,
            "Metadata": {
                "document-id": document_id,
                "expires-at": expires_at.isoformat(),
            },
            "Expires": expires_at,
        }
        put_kwargs.update(self._encryption_kwargs())
        self.client.put_object(**put_kwargs)

        return StoredTemporaryDocument(
            document_id=document_id,
            key=key,
            content_type=content_type,
            size_bytes=len(content),
            expires_at=expires_at,
        )

    def get_document(self, document_id: str) -> bytes:
        self.assert_configured()
        response = self.client.get_object(
            Bucket=self.settings.s3_temp_bucket,
            Key=self.build_key(document_id),
        )
        return response["Body"].read()

    def delete_document(self, document_id: str) -> None:
        self.assert_configured()
        self.client.delete_object(
            Bucket=self.settings.s3_temp_bucket,
            Key=self.build_key(document_id),
        )

    def build_key(self, document_id: str) -> str:
        if not fullmatch(r"[a-f0-9]{32}", document_id):
            raise ValueError("Invalid temporary document id")
        return f"{TEMPORARY_DOCUMENT_PREFIX}/{document_id}"

    def _encryption_kwargs(self) -> dict[str, str]:
        if self.settings.kms_key_id:
            return {
                "ServerSideEncryption": "aws:kms",
                "SSEKMSKeyId": self.settings.kms_key_id,
            }
        return {"ServerSideEncryption": "AES256"}
