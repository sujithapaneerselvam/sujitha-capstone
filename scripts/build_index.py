"""Week 6 - build the RAG index once and cache it to data/embeddings.json.

Reads data/corpus/*.md, chunks + embeds every chunk, writes the index. Re-run
only when the corpus changes.

  real:     OPENAI_API_KEY set  ->  text-embedding-3-small
  offline:  USE_FAKE=1 python scripts/build_index.py  (hashing embedding, flow only)

Usage:  python scripts/build_index.py
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.rag.naive_rag import build_index, save_index, INDEX_PATH, CORPUS_DIR
import argparse
def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description = "Build a rag"
  )
  parser.add_argument(
    "--corpus",
    default = CORPUS_DIR,
    help = "Directory contaning corpus files",
  )
  parser.add_argument(
    "--size",
    type = int,
    default = 500,
    help ="size of the chunks in characters",
  )
  parser.add_argument(
    "--overlap",
    type = int,
    default=50,
    help = "chunk overlap in characters ",
  )
  parser.add_argument(
    "--out",
    default = INDEX_PATH,
    help ="output index json file",
  )
  return parser.parse_args()

def main() -> None:
  args = parse_args()
  index = build_index(corpus_dir=args.corpus, size=args.size, overlap=args.overlap,)
  save_index(index, args.out)
  sources = sorted({c["source_id"] for c in index})
  print(f"Indexed {len(index)} chunks from {len(sources)} docs -> {args.out} ")
  print("sources:", ", ".join(sources))


if __name__ == "__main__":
    main()
