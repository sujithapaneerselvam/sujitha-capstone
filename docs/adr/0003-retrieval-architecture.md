# ADR 0003 — Retrieval Architecture

## Status
Accepted for M2 (Week 12); retrieval tuning remains open

## Date
Originally drafted in W7; revised in W9 and W12.

## Context
We need to choose an embedding model, chunking strategy, and vector store
for our RAG pipeline. The choices affect retrieval quality (hit rate),
operational cost (API spend), and latency (user-facing response time).

In Week 7, we compared text-embedding-3-small and text-embedding-3-large on the 20-question BrightPath golden set using top-k 10.

## Decision
### Retrieval and reranking — W9 to M2

The Week 12 BrightPath evaluation used `text-embedding-3-small`,
Qdrant collection `capstone_chunks_v2`, and KB version `v2.w10`.
The pipeline combines dense retrieval and BM25 using reciprocal rank
fusion, then uses a cross-encoder to select the final three passages.
Answers cite the numbered passages supplied to the model.

On 20 live questions, faithfulness was 0.8720, answer relevance was
0.7108, context precision was 0.7417, and context recall was 0.5625.
These scores describe the full pipeline. They do not isolate the
improvement from hybrid retrieval or reranking.

The broad business-expense question retrieved medical reimbursement
evidence and produced an off-topic answer. Naming the Travel and
Expense Policy retrieved the correct guidance. Keep the original
wording as a regression case and compare candidates before and after
reranking to locate where the correct passage was lost.


### Week 7 embedding comparison

| Model | Run ID | Expected-source hits (answerable only) | Mean latency | Recorded pipeline cost/query |
|---|---|---:|---:|---:|
| `text-embedding-3-small` | `1788355592` | 16/16 | 2,733.80 ms | $0.000167 |
| `text-embedding-3-large` | `1788355888` | 16/16 | 2,487.78 ms | $0.000165 |

Both runs used top-k 10 and recorded 16 hits across 20 questions.
The four questions without expected sources are assessed separately
for abstention. The run using the large model had about 9% lower mean pipeline latency in this comparison,
but one run per model does not establish a consistent speed advantage.
The recorded pipeline costs do not establish the cost of embedding.

M2 retained `text-embedding-3-small`: the large model showed no
expected-source hit-rate improvement on this benchmark. The local
model remains an alternative; no local-model result was recorded
in this comparison.

### Chunking and ingestion

Week 6 recommended 300-character chunks with 30-character overlap.
The 300/30, 500/50, and 800/80 runs each achieved 16/16 expected-source
hits on answerable questions. The 300/30 run had the lowest mean latency
(1,845.60 ms) and recorded total cost ($0.001761). Q08 still abstained
despite retrieving the expected document.

The Week 7 draft proposed sentence-aware chunking with a target of
about 400 characters. Week 8 introduced structure-aware chunking.
The Week 8 audit records 12 files and 313 chunks in
`capstone_chunks_v2`. The exact chunk size, overlap, and boundary rules
used to build the collection evaluated at M2 remain unverified.

### Vector store

The live M2 run used Qdrant Cloud, collection `capstone_chunks_v2`,
with KB version `v2.w10`. Chroma was the lab default and is an alternative.
## Alternatives Considered

| Area | Alternative | Decision and rationale |
|---|---|---|
| Embeddings | `text-embedding-3-large` | Both models achieved 16/16 expected-source hits. Retained the small model for M2. |
| Embeddings | Local `all-MiniLM-L6-v2` | Considered for offline use; no result was recorded in this comparison. |
| Chunking | 500/50 and 800/80 | Both tied with 300/30 on expected-source hits but had higher mean latency and recorded total cost in Week 6. |
| Vector store | Chroma | Lab default; the live M2 run used Qdrant Cloud. |

## Consequences

- The deployed pipeline depends on OpenAI for embeddings and Qdrant Cloud for vector retrieval.
- For M2, improving retrieval coverage takes priority over changing the embedding model.

## Open Issues and Next Experiment
**Next experiment: broad expense-query regression.** Rerun the original
business-expense question with the cache disabled. Check whether the
relevant Travel and Expense Policy passage is missing from the initial
candidates or is dropped during reranking. If it is missing initially,
investigate retrieval; if it drops out later, investigate reranking.
Change one setting at a time and verify that the original question
returns a supported answer with a citation to the correct policy.

**Future work**

- Compare small and large embeddings with the same hybrid retrieval settings.
- Measure whether cross-encoder reranking improves retrieval with the small model.
- Evaluate reduced embedding dimensions (for example, 512).
- Assess whether a local embedding model meets data-sovereignty requirements.


## Evaluation Evidence

- [Week 6 chunking experiment](../runs/week6-chunking-experiment.md)
- [Week 7 embedding comparison](../runs/week7-embedding.md)
- [Week 8 ingestion and PII audit](../runs/week8-pii-audit.md)
- [Week 12 KPI snapshot](../kpi/wk12-snapshot.md)