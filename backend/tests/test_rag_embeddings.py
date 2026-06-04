import pytest

from app.rag.embeddings import LocalHashEmbeddingProvider, cosine_similarity, tokenize


def test_tokenize_normalizes_spanish_text() -> None:
    assert tokenize("Horas extra y acción sindical.") == [
        "horas",
        "extra",
        "y",
        "acción",
        "sindical",
    ]


def test_local_hash_embeddings_are_deterministic_and_normalized() -> None:
    provider = LocalHashEmbeddingProvider(dimensions=16)

    first = provider.embed(["horas extra"])[0]
    second = provider.embed(["horas extra"])[0]

    assert first == second
    assert sum(value * value for value in first) == pytest.approx(1.0)


def test_empty_text_returns_zero_vector() -> None:
    provider = LocalHashEmbeddingProvider(dimensions=4)

    assert provider.embed([""])[0] == [0.0, 0.0, 0.0, 0.0]


def test_cosine_similarity_rejects_different_dimensions() -> None:
    with pytest.raises(ValueError, match="misma dimension"):
        cosine_similarity([1.0], [1.0, 0.0])
