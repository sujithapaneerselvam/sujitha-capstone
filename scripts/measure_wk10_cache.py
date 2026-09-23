"""Measure cost + latency delta from W9 → W10 (with caching).

Runs the golden set twice:
  Pass 1 (cold): cache empty; every query pays full RAG cost
  Pass 2 (warm): cache primed; ideally every query hits
"""
import json, time
from pathlib import Path

from src.rag.qdrant_rag import ask_rag
from src.rag import cache

GOLDEN = Path("data/golden_set.jsonl")
golden = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l]

# Prices per 1M tokens (Aug 2026 — verify)
PRICING = {
    "input":       0.15,
    "output":      0.60,
    "input_cached":0.075,
    "embed":       0.02,
}

def cost_of(res: dict, q_len_tokens: int) -> float:
    if res["cache_hit"]:
        # Only paid for the query embedding
        return q_len_tokens * PRICING["embed"] / 1_000_000
    fresh = res["n_input_tokens"] - res["n_cached_input_tokens"]
    return (
        res["n_cached_input_tokens"] * PRICING["input_cached"] / 1_000_000
        + fresh                      * PRICING["input"]        / 1_000_000
        + res["n_output_tokens"]     * PRICING["output"]       / 1_000_000
        + q_len_tokens               * PRICING["embed"]        / 1_000_000
    )

def run_pass(label):
    latencies, cost = [], 0.0
    n_hits, n_misses = 0, 0
    for q in golden:
        t0 = time.time()
        res = ask_rag(q["question"])
        latencies.append((time.time() - t0) * 1000)
        cost += cost_of(res, q_len_tokens=len(q["question"].split()))
        if res["cache_hit"]: n_hits += 1
        else: n_misses += 1
    latencies.sort()
    return {"label": label, "cost": cost,
            "p50_ms": latencies[len(latencies)//2],
            "p95_ms": latencies[int(len(latencies)*0.95)],
            "hits": n_hits, "misses": n_misses}

cache.clear()
cold = run_pass("cold")
warm = run_pass("warm")

print(f"══ W10 cost + latency ══\n")
print(f"  {'Pass':<8s} {'hits':>5s} {'p50':>7s} {'p95':>7s} {'total cost':>12s}")
for p in [cold, warm]:
    print(f"  {p['label']:<8s} {p['hits']:>5d} {p['p50_ms']:>6.0f}ms {p['p95_ms']:>6.0f}ms  ${p['cost']:>10.5f}")

if cold['cost']:
    saved_pct = 100 * (cold['cost'] - warm['cost']) / cold['cost']
    print(f"\n  Warm-pass cost saved: {saved_pct:.1f}%")

# Save numbers to wk10-snapshot.md (create the file per template below)