from pathlib import Path

from app.rag.chunking import SourceDocument, chunk_document
from app.rag.loader import load_corpus


def ingest_document(document: SourceDocument) -> int:
    chunks = chunk_document(document)
    return len(chunks)


def ingest_corpus_manifest(manifest_path: str) -> int:
    corpus = load_corpus(manifest_path=Path(manifest_path))
    return sum(ingest_document(document) for document in corpus.documents)
