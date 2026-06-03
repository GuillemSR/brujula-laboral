from app.rag.chunking import SourceDocument, chunk_document


def ingest_document(document: SourceDocument) -> int:
    chunks = chunk_document(document)
    return len(chunks)
