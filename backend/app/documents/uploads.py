from dataclasses import dataclass
from pathlib import PurePosixPath
from re import sub
from uuid import uuid4

from app.core.config import Settings


ALLOWED_CONTENT_TYPES = {
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
}


class DocumentUploadError(ValueError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ValidatedUpload:
    document_id: str
    filename: str
    content_type: str
    content: bytes
    size_bytes: int


def validate_upload(
    filename: str | None,
    content_type: str | None,
    content: bytes,
    settings: Settings,
) -> ValidatedUpload:
    size_bytes = len(content)
    if size_bytes == 0:
        raise DocumentUploadError("El documento no puede estar vacio.")
    if size_bytes > settings.temp_document_max_bytes:
        raise DocumentUploadError("El documento supera el tamano maximo permitido.", 413)

    normalized_filename = normalize_filename(filename)
    suffix = PurePosixPath(normalized_filename).suffix.lower()
    if suffix not in ALLOWED_CONTENT_TYPES:
        raise DocumentUploadError("Tipo de documento no admitido.", 415)

    normalized_content_type = content_type or "application/octet-stream"
    if normalized_content_type not in ALLOWED_CONTENT_TYPES[suffix]:
        raise DocumentUploadError("El tipo MIME no coincide con la extension admitida.", 415)

    return ValidatedUpload(
        document_id=uuid4().hex,
        filename=normalized_filename,
        content_type=normalized_content_type,
        content=content,
        size_bytes=size_bytes,
    )


def normalize_filename(filename: str | None) -> str:
    raw_name = (filename or "documento").replace("\\", "/").split("/")[-1].strip()
    if not raw_name:
        raw_name = "documento"

    path = PurePosixPath(raw_name)
    suffix = path.suffix.lower()
    stem = path.stem if suffix else raw_name
    safe_stem = sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    if not safe_stem:
        safe_stem = "documento"

    return f"{safe_stem}{suffix}"
