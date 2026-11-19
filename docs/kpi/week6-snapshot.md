# Week 6 — RAG Chunking Experiment

## Experiment setup

I have evaluated three chunking configurations using the same 20-question golden set.
 The small index used a chunk size of 300 characters with 30-character overlap.
 The medium index used 500/50, and the large index used 800/80.

## Results

| Strategy | Chunk size (chars) | Overlap (chars) | Run ID | Expected-source hits (all questions) | Expected-source hit rate (answerable only) | Mean latency (ms) | Recorded total cost (USD) |
|---|---:|---:|---|---:|---:|---:|---:|
| Small | 300 | 30 | `1787823347` | 16/20 | 16/16 (100%) | 1845.60 | $0.001761 |
| Medium | 500 | 50 | `1787839193` | 16/20 | 16/16 (100%) | 2197.40 | $0.002092 |
| Large | 800 | 80 | `1787839289` | 16/20 | 16/16 (100%) | 2341.25 | $0.002746 |


Q17–Q20 had no expected source document. The evaluation recorded a zero
retrieval hit for those rows by design, so the raw count was 16/20. Among
questions with an expected source, all three configurations achieved 16/16.
Assess abstention separately for Q17–Q20; this table does not report its results.

## Conclusion

The Week 6 recommendation was 300-character chunks with 30-character overlap.
All three configurations tied at 16/16 expected-source hits on answerable
questions. The 300/30 run had the lowest mean latency (1,845.60 ms) and recorded
total cost ($0.001761). Q08 still abstained despite retrieving the expected
document, so the results do not establish an answer-quality advantage.