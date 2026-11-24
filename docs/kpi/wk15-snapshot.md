# Week 15 — Memory KPI Snapshot

Evaluation: 20 BrightPath questions, memory OFF and ON; 40 live runs.
Review: AI-assisted corpus-based assessment.

| Measure | OFF | ON |
|---|---:|---:|
| Complete factual correctness | 13/20 | 13/20 |
| Corpus-supported claims | 17/20 | 18/20 |
| Precise source attribution | 12/20 | 14/20 |
| Bullet-format adherence | 5/20 | 20/20 |
| Successful policy calls | 20/20 | 20/20 |
| Mean outer-agent prompt characters | 1665.8 | 1957.1 |
| Latency P50 (ms) | 9060.5 | 9942.5 |
| Latency P95 (ms) | 11257.0 | 12140.6 |
| Actual API cost | Unmeasured | Unmeasured |

Prompt-character proxy increased by 17.5%.
Grounding is corpus-based review, not RAGAS or exact retrieved-chunk
validation. Single-run latency differences are observational.

Evidence:
- ../../eval/logs/wk15-brightpath-memory-full.json
- ../../eval/logs/wk15-brightpath-memory-full-reviewed.json
- ../../eval/logs/wk15-brightpath-memory-review.md