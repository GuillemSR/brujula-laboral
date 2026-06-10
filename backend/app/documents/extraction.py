from dataclasses import dataclass


TEXT_CONTENT_TYPES = {
    "text/plain",
    "text/markdown",
    "application/octet-stream",
}


@dataclass(frozen=True)
class ExtractedDocument:
    filename: str
    text: str


class DocumentExtractionError(ValueError):
    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


def extract_text(
    filename: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> ExtractedDocument:
    """Extract text from an uploaded private document.

    The initial implementation only accepts plain text. PDF/DOCX extraction will be added
    after the privacy and deletion flow is verified.
    """
    if content_type not in TEXT_CONTENT_TYPES:
        raise DocumentExtractionError("El formato del documento todavia no permite extraer texto.")

    text = content.decode("utf-8", errors="replace")
    if not text.strip():
        raise DocumentExtractionError("No se ha podido extraer texto util del documento.")

    return ExtractedDocument(filename=filename, text=text)
