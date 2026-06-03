from dataclasses import dataclass

from app.rag.chunking import Chunk


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float


class Retriever:
    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        raise NotImplementedError("Retriever backend is not configured yet")
