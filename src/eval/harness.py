"""src/eval/harness.py — build eval rows, synthetic (offline) or live (W11).

Row shape: {"id", "question", "answer", "contexts": [str,...], "ground_truth",
            "cache_hit", "latency_ms", "cost_usd", "notes"}
"""
from __future__ import annotations

import json
from pathlib import Path

from src.eval.golden import GoldenEntry, load_golden
from src.eval.ragas_metrics import offline_mode

GOLDEN_PATH = Path("data/golden_set.jsonl")
OFFLINE_KB_VERSION = "v2.w10"

_DISTRACTOR = (
    "The office kitchen is restocked every Monday morning and the building "
    "reception desk is open from eight until six."
)


def _split_two(text: str) -> tuple[str, str]:
    words = text.split()
    mid = max(1, len(words) // 2)
    return " ".join(words[:mid]), " ".join(words[mid:])


def _synth_row(entry: GoldenEntry, index: int) -> dict:
    """Build one synthetic row. Most healthy; g019/g015/g005 are degraded."""
    gt = entry.ideal_answer if isinstance(entry.ideal_answer, str) else json.dumps(entry.ideal_answer)
    c1, c2 = _split_two(gt)
    contexts = [c1, c2, _DISTRACTOR]
    answer = gt

    if entry.id == "g019":
        answer = gt + (" The company also matches up to five percent of salary "
                       "into a managed crypto retirement fund.")
    elif entry.id == "g015":
        contexts = [c1, _DISTRACTOR]
    elif entry.id == "g005":
        contexts = [c1[:max(1, len(c1) // 2)], _DISTRACTOR]

    cache_hit = index < 13
    return {
        "id":           entry.id,
        "question":     entry.question,
        "answer":       answer,
        "contexts":     contexts,
        "ground_truth": gt,
        "cache_hit":    cache_hit,
        "latency_ms":   184 if cache_hit else 785,
        "cost_usd":     0.000041 if cache_hit else 0.000412,
        "notes":        entry.notes,
    }


def _live_rows(golden: list[GoldenEntry]) -> list[dict]:
    from time import perf_counter

    from api.main import (
        COLLECTION, EMBED_MODEL, KB_VERSION, LLM_MODEL,
        _ensure_bm25, _get_qdrant,
    )
    from src.rag import retrieval

    client = _get_qdrant()
    if client is None:
        raise RuntimeError("Could not initialize Qdrant. Load .env in this shell.")

    _ensure_bm25()
    if retrieval._bm25_index is None:
        raise RuntimeError("BM25 initialization failed. Check the warning above.")

    rows = []
    for entry in golden:
        started = perf_counter()
        result = retrieval.ask_rag(
            entry.question,
            client,
            collection=COLLECTION,
            retrieval_method="hybrid_rerank",
            k_final=3,
            model=EMBED_MODEL,
            llm_model=LLM_MODEL,
        )
        rows.append({
            "id": entry.id,
            "question": entry.question,
            "answer": result["answer"],
            "contexts": result["contexts"],
            "ground_truth": entry.ideal_answer,
            "cache_hit": False,
            "latency_ms": round((perf_counter() - started) * 1000),
            "cost_usd": result.get("cost_usd"),
            "kb_version": KB_VERSION,
            "notes": entry.notes,
        })
    return rows

def active_kb_version() -> str:
    if offline_mode():
        return OFFLINE_KB_VERSION

    from api.main import KB_VERSION
    return KB_VERSION

def build_rows(golden: list[GoldenEntry] | None = None) -> list[dict]:
    """The eval rows under test — synthetic (offline) or live."""
    golden = golden or load_golden(GOLDEN_PATH)
    if offline_mode():
        return [_synth_row(e, i) for i, e in enumerate(golden)]
    return _live_rows(golden)
