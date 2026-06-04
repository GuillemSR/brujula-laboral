from app.rag.retrieval import RetrievalResult


def format_context(results: list[RetrievalResult]) -> str:
    blocks: list[str] = []
    for index, result in enumerate(results, start=1):
        source = result.chunk.metadata.source
        blocks.append(
            "\n".join(
                [
                    f"[{index}] {result.chunk.citation_label}",
                    source.source_url.unicode_string(),
                    result.chunk.text,
                ]
            )
        )
    return "\n\n".join(blocks)


def format_citation_list(results: list[RetrievalResult]) -> list[str]:
    return [
        f"[{index}] {result.chunk.citation_label}" for index, result in enumerate(results, start=1)
    ]
