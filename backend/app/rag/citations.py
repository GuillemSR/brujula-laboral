from app.rag.retrieval import RetrievalResult


def format_context(results: list[RetrievalResult]) -> str:
    blocks: list[str] = []
    for index, result in enumerate(results, start=1):
        title = result.chunk.metadata.get("title", result.chunk.source_id)
        url = result.chunk.metadata.get("source_url", "")
        blocks.append(f"[{index}] {title}\n{url}\n{result.chunk.text}")
    return "\n\n".join(blocks)
