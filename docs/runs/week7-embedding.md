| Metric                      |  Small model |  Large model |
| --------------------------- | -----------: | -----------: |
| Run ID                      | `1788355592` | `1788355888` |
| Top-k                       |           10 |           10 |
| Questions                   |           20 |           20 |
| Document hits               |        16/20 |        16/20 |
| Reported hit rate           |          80% |          80% |
| Average latency             |   2733.80 ms |   2487.78 ms |
| P50 latency                 |   2323.63 ms |   2239.18 ms |
| Total recorded cost         |    $0.003337 |    $0.003292 |
| Average recorded cost/query |    $0.000167 |    $0.000165 |


Both runs achieved the same document-hit count: 16/16 among questions with expected sources. The four missing-information questions require separate answer review.
The second run had approximately 9% lower average latency, but one run per model is insufficient to establish a consistent speed advantage.
These metrics alone do not confirm that Q08 and Q09 improved or that Q18 avoided unsupported claims. Check their full answers before choosing the final model.
Label the costs recorded pipeline costs; don’t claim they include embedding charges unless your code accounts for them.
