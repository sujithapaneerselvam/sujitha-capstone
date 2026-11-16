# Week 12 — Real RAG Debugging Investigation
## Repeated-query cache verification

| Measurement | First VPN request | Repeated VPN request |
|---|---:|---:|
| Cache hit | false | true |
| Retrieval method | hybrid_rerank | cache |
| Chunks used | 3 | 0 |
| Latency | 56,080 ms | 504 ms |
| Returned citation entries | 3 | 0 |

The repeated request returned the same answer in approximately 0.50 seconds.
This confirms cache reuse for this question. It is a single cold/warm pair,
not an aggregate latency benchmark.

The cached answer retains [1], but its citation mapping is missing.
Preserving citation metadata remains pending. Reported cost is zero because
usage-cost accounting has not been verified.

Added an optional use_cache query parameter to isolate the full pipeline. With use_cache=false, the API returned the correct annual-leave answer using hybrid_rerank and three chunks. Reported latency was 57,396 ms. A previous cached request took 444 ms. These are individual observations, not percentile benchmarks; uncached latency after warm-up remains to be checked.


The uncached request completed with HTTP 200, but the final context came from the Employee Benefits Guide and Code of Conduct. The answer gave medical claim requirements for a business expense question. Verification against the expense policy and inspection of pre-rerank candidates are pending.

| Uncached request | Reported latency | Result |
|---|---:|---|
| Broad business-expense question, first request | 171,081 ms | Failed: cited medical benefits and gave medical claim requirements |
| Same broad question, repeated without restarting | 34,251 ms | Failed again: same wrong policy and answer |
| Specific business-trip expense-report question | 2,675 ms | Passed: correct fields and deadline, with the travel and expense policy cited |