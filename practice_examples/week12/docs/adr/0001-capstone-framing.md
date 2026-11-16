# ADR 0001 — Capstone Framing — v2 (M2)

*(Prior W1–W11 entries elided — keep your repo's full text. This is the Phase-2
consolidation the milestone asks for: every decision in one table.)*

## Phase 2 consolidated decisions (v2 · M2)

| Area | Decision | Why |
|---|---|---|
| Chunking | 512-token, 64 overlap | balances recall vs precision |
| Hybrid weight | BM25 0.4 + dense | catches exact-term queries |
| Reranker + top-K | cross-encoder, top-K 3 | lifts context precision; small prompt |
| Cache | semantic (0.95) + tombstones | cost win, safe deletes |
| Eval | RAGAS thresholds (faithfulness 0.85, recall 0.80, ...) | defensible bar |
| KPIs | 8-KPI dashboard, kb_version-tagged | portfolio evidence |

Status: **v2 (M2)** — Phase 2 closed; retrieval + KB-lifecycle decisions consolidated.
