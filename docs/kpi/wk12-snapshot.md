# W12 KPI Snapshot (M2)
**eval_mode:** `live`  
**kb_version:** `v2.w10`  
**golden_set:** 20 BrightPath entries (`data/brightpath_golden.jsonl`)


## 8-KPI dashboard snapshot

Live evaluation: 20 BrightPath questions, KB `v2.w10`.

| KPI ID | KPI | Value | Notes |
|---|---|---|---|
| KPI 1 | Task success rate | Not measured | Requires separate task-success scoring |
| KPI 2 | Grounded response rate | 0.8720 | Live RAGAS faithfulness |
| KPI 3 | Hallucination rate | 0.1280 | Unsupported-claim proxy: 1 − faithfulness; not an answer-level rate |
| KPI 4 | Retrieval hit rate | Not measured | Correct supporting chunk in top-k; distinct from context precision |
| KPI 5 | Tool success rate | N/A | Tools are outside this milestone |
| KPI 6 | Cost per query (USD) | Not measured | Usage cost was not verified |
| KPI 7 | Latency P50 / P95 (ms) | Not yet calculated | Calculate from the saved request timings |
| KPI 8 | Escalation rate | N/A | Human escalation is outside this milestone |

Supporting live metrics: answer relevance **0.7108**, context precision
**0.7417**, and context recall **0.5625**. All four RAGAS metrics scored
all 20 questions. Faithfulness met its provisional threshold; the other
three fell below theirs. The relevance judge returned one generation
instead of the requested three.