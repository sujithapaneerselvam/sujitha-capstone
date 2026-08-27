# Week 6 — RAG Chunking Experiment

## Experiment setup

I have evaluated three chunking configurations using the same 20-question golden set.
 The small index used a chunk size of 300 characters with 30-character overlap.
 The medium index used 500/50, and the large index used 800/80.

## Results

| Strategy | Chunk size | Overlap | Run ID | Retrieval hits | Answerable hit rate | Average latency | Total cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Small | 300 | 30 | 1787823347 | 16/20 | 16/16 (100%) | 1845.60 ms | $0.001761 |
| Medium | 500 | 50 | 1787839193 | 16/20 | 16/16 (100%) | 2197.40 ms | $0.002092 |
| Large | 800 | 80 | 1787839289 | 16/20 | 16/16 (100%) | 2341.25 ms | $0.002746 |

The four questions without expected source documents were Q17–Q20. 
Therefore, they received a retrieval hit of zero by design and were evaluated separately for correct abstention.

## Observations

All three chunking strategies retrieved an expected source for every answerable question. The small-chunk configuration had the lowest average latency and total cost. Medium and large chunks did not improve the retrieval hit rate, but they increased latency and cost.

Retrieval success did not always guarantee answer correctness. For example, in the small-index run, Q08 retrieved the correct lost-device procedure but still answered that there was not enough information. Some multi-document answers were also incomplete. Therefore, answer quality must be considered separately from retrieval hit rate.

## Conclusion

Based on the current results, I would select the small-chunk configuration. It achieved the same 100% retrieval hit rate on answerable questions as the other configurations while recording the lowest latency and cost. However, I would also review answer completeness before making the final production recommendation.