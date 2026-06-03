from dataclasses import dataclass


@dataclass(frozen=True)
class TemporaryDocumentContext:
    filename: str
    text: str


def build_temporary_context(filename: str, text: str) -> TemporaryDocumentContext:
    return TemporaryDocumentContext(filename=filename, text=text)
