import hashlib
import math
import re
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding per input text."""


TOKEN_PATTERN = re.compile(r"[a-záéíóúüñ0-9]+", re.IGNORECASE)
DEFAULT_EMBEDDING_DIMENSIONS = 128


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


class LocalHashEmbeddingProvider:
    """Small deterministic embedding provider for local RAG prototypes."""

    def __init__(self, dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions debe ser mayor que cero.")
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Los vectores deben tener la misma dimension.")
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


class NotConfiguredEmbeddingProvider:
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("Embedding provider is not configured yet")
