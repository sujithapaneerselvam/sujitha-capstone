| Week 16 metric | Result | Rate |
|---|---:|---:|
| Factual correctness | 12/20 | 60.0% |
| Corpus grounding | 15/19 | 78.9% |
| Citation validity | 13/19 | 68.4% |
| Bullet preference followed | 20/20 | 100% |
| Successful policy calls | 19/19 attempted | 100% |

Both agents used gpt-5-mini with memory ON for the same 20 questions. The Week 16 graph followed the bullet preference on every answer, but only 12 answers met the factual correctness criterion. For q17, the graph asked for a city already supplied and made no policy call. This counted as a factual miss; grounding and citation validity were marked N/A. Median latency was 15,397.0 ms, compared with 9,942.5 ms in Week 15. Actual API cost was unmeasured.