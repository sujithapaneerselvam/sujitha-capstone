"""Update one text or Markdown document in the capstone KB.

Run from the repository root:
    python3 -m scripts.update_document data/corpus/example.txt
"""
import sys
from pathlib import Path

from src.pipeline.pipeline import ingest_or_update_source
from src.rag.qdrant_store import load_store


def main(doc_path: str) -> None:
    path = Path(doc_path)

    if not path.is_file():
        raise SystemExit(f"Document not found: {path}")

    if path.suffix.lower() not in {".txt", ".md"}:
        raise SystemExit("This updater currently supports .txt and .md files only")

    body = path.read_text(encoding="utf-8")
    if len(body.strip()) < 50:
        raise SystemExit("Document is empty or too short; no update performed")

    store = load_store()
    if store.collection != "capstone_chunks_v2":
        raise SystemExit(
            f"Wrong collection: {store.collection}; expected capstone_chunks_v2"
        )

    result = ingest_or_update_source(store, path.name, body)

    print(f"Update complete for {path.name}:")
    print(f"  Tombstoned: {result['tombstoned']} old chunks")
    print(f"  Ingested: {result['ingested']} new chunks")
    print(f"  Cache cleared: {result['cache_cleared']} entries")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 -m scripts.update_document <document-path>"
        )
    main(sys.argv[1])