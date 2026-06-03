from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedDocument:
    filename: str
    text: str


def extract_text(filename: str, content: bytes) -> ExtractedDocument:
    """Extract text from an uploaded private document.

    The initial implementation only accepts plain text. PDF/DOCX extraction will be added
    after the privacy and deletion flow is verified.
    """
    text = content.decode("utf-8", errors="replace")
    return ExtractedDocument(filename=filename, text=text)
