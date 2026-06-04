import argparse
from pathlib import Path

from app.rag.ingest import ingest_corpus_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida y carga el corpus local inicial.")
    parser.add_argument(
        "manifest",
        nargs="?",
        default="corpus/sources.example.json",
        help="Ruta al manifiesto JSON de fuentes.",
    )
    args = parser.parse_args()

    chunk_count = ingest_corpus_manifest(str(Path(args.manifest)))
    print(f"Corpus cargado: {chunk_count} chunks generados.")


if __name__ == "__main__":
    main()
