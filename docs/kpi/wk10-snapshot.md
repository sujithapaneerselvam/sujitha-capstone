# Week 10 — Semantic cache and document lifecycle

## Measurement

The same 20 golden-set questions were run twice through
`src.rag.qdrant_rag.ask_rag()`. The cache was cleared before the cold
pass and retained for the immediately following warm pass.

| Metric | Cold pass | Warm pass |
|---|---:|---:|
| Questions | 20 | 20 |
| Semantic cache hits | 0/20 | 20/20 |
| Cache hit rate | 0% | 100% |
| p50 latency | 2,099 ms | 389 ms |
| p95 latency | 3,339 ms | 494 ms |
| Estimated total cost | $0.00158 | $0.00001 |

The measurement script reported 99.6% estimated warm-pass cost savings.
p50 latency decreased by approximately 81.5%; p95 decreased by
approximately 85.2%. These results describe an immediately repeated
20-question workload, not an expected production cache hit rate.
Costs are estimates from the measurement script; warm requests still
embed the question.

## Document update verification

Updating `HR_02_Annual_Leave_Policy.txt` tombstoned 26 old chunks,
inserted 26 new chunks, and cleared two cache entries. Verification
found 52 total versions: 26 live and 26 tombstoned. The first question
after the update was a cache miss and returned the current 20-day
entitlement; the repeated question was a cache hit with the same answer.

## Limitations

Cached responses currently contain the answer but do not preserve
source metadata (`sources=[]`). Cold or cache-bypassed responses must
be used for source and grounding evaluation. The HTTP `/ask_batched`
endpoint still uses its separate retrieval and answer pipeline, so
these cache measurements apply to direct `ask_rag()` calls.