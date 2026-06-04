from dataclasses import dataclass
from pathlib import Path

from app.rag.chunking import Chunk, chunk_document
from app.rag.embeddings import EmbeddingProvider, LocalHashEmbeddingProvider, cosine_similarity
from app.rag.loader import load_corpus


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float


class Retriever:
    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        raise NotImplementedError("Retriever backend is not configured yet")


@dataclass(frozen=True)
class IndexedChunk:
    chunk: Chunk
    embedding: list[float]


class LocalRetriever(Retriever):
    def __init__(
        self,
        chunks: list[Chunk],
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider or LocalHashEmbeddingProvider()
        embeddings = self.embedding_provider.embed([chunk.text for chunk in chunks])
        self.index = [
            IndexedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]

    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        if top_k <= 0:
            return []

        query_embedding = self.embedding_provider.embed([query])[0]
        results = [
            RetrievalResult(
                chunk=indexed.chunk,
                score=cosine_similarity(query_embedding, indexed.embedding),
            )
            for indexed in self.index
        ]
        results.sort(key=lambda result: result.score, reverse=True)
        return results[:top_k]


def build_local_retriever(manifest_path: Path) -> LocalRetriever:
    corpus = load_corpus(manifest_path)
    chunks = [chunk for document in corpus.documents for chunk in chunk_document(document)]
    return LocalRetriever(chunks=chunks)
