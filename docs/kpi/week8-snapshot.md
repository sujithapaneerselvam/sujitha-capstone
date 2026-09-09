# Week 8 KPI Snapshot

## Configuration

- Week 7 collection: `capstone_chunks`
- Week 8 collection: `capstone_chunks_v2`
- Embedding model: `text-embedding-3-small`
- Embedding dimensions: 1536
- Retrieval top-k: 10
- Corpus files: 12
- Week 8 collection size: 313 chunks

## Week 7 versus Week 8

| Metric | Week 7 baseline | Week 8 ingestion |
| --- | ---: | ---: |
| Run ID | `1788355592` | `1788945108` |
| Questions evaluated | 20 | 20 |
| Retrieval hits | 16/20 | 16/20 |
| Reported hit rate | 80% | 80% |
| Questions with expected sources | 16 | 16 |
| Expected-source hits | 16/16 | 16/16 |
| Average latency | 2733.80 ms | 2263.48 ms |
| Total recorded cost | $0.003337 | $0.003286 |
| Average recorded cost/query | $0.000167 | $0.000164 |

## Interpretation

The Week 8 ingestion pipeline preserved the Week 7 retrieval result. Both
runs retrieved at least one expected document for all 16 questions that
define an `expected_source`.

Questions Q17 through Q20 intentionally have empty expected-source lists
because they test missing-information behaviour. The evaluator records these
questions as `hit=0`. Therefore, the reported result is 16/20, while the
expected-source hit rate among eligible questions is 16/16.

The Week 8 run had approximately 17.2% lower average latency than the Week 7
baseline. Its total recorded cost was approximately 1.5% lower. Because these
figures compare only one run from each configuration, they do not establish a
consistent performance improvement.

The recorded costs represent costs reported by the answer-generation
pipeline. They may not include ingestion embedding charges or query embedding
charges.

## Ingestion quality observations

The Week 8 ingestion pipeline successfully preserved important policy facts,
including annual-leave durations, deadlines, accrual values, dates, and
locations after correcting the PII entity allowlist.

A reproducible manual sample also revealed several heading-only chunks, such
as `STANDARD PROCEDURE` and `RELATED DOCUMENTS`. These chunks provide limited
standalone semantic value and could reduce retrieval quality. A future
improvement is to merge very short heading chunks with the following content.

## Conclusion

The Week 8 pipeline introduced structured parsing, recursive chunking, PII
scrubbing, metadata enrichment, embedding generation, and Qdrant upsert
without reducing expected-source retrieval performance. The corrected
configuration is suitable as the next capstone ingestion baseline.