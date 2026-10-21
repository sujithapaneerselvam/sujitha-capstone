# Week 11 Activity — Diagnose the Broken Eval Report


## 1. Diagnose

| Symptom | Layer | Likely cause | Evidence to confirm |
|---|---|---|---|
| g019 invents a 5% crypto benefit; faithfulness 0.20 | Generation | Answer exceeds the available evidence | Compare answer claims with retrieved passages and grounding instructions |
| g015 omits the meetings requirement; recall 0.33 | Retrieval | Second-hop evidence was not retrieved | Inspect required passages against retrieved top-k |
| g004, g008 and g011 contain two irrelevant passages in top-three | Retrieval | Ranking admits distractors | Inspect candidate scores and reranking results |
| Cache-hit accuracy 0.70 is below cache-miss accuracy 0.83 | Cache | Possibly stale answers or incorrect semantic matches | Inspect matched questions, similarity scores, KB versions and invalidation logs |
| Previously repeated questions now miss; hit rate 12% | Cache | Possible expiry, invalidation or changed lookup configuration | Compare query keys, expiry, embeddings and cache logs across runs |
| Evaluation mixes v2.w10 and v3.w11 | Process | Documents changed during evaluation | Inspect row-level KB tags and ingestion timestamps |
| All quality thresholds are 0.30 | Process | Permissive gates allow poor quality to pass | Compare thresholds with a reviewed, repeated baseline |
| Tool success and escalation are reported as zero | Reporting | Unimplemented features are treated as failed executions | Confirm feature availability; report N/A |
| 1 − faithfulness is labelled hallucination rate | Reporting | Claim-level proxy is confused with answer-level failure rate | Check metric definitions and denominators |
| Context precision is labelled retrieval hit rate | Reporting | Two different retrieval measures are conflated | Separate passage relevance from correct-chunk presence in top-k |

These are diagnostic hypotheses; traces and logs are needed to confirm causes.

## 2. Prescribe

- Generation: enforce context-only answers and abstention; retest g019.
- Retrieval recall: test query expansion or increased top-k for multi-hop questions.
- Retrieval precision: test ranking or reranking changes against the golden set.
- Cache correctness: verify semantic matches and invalidate entries after KB updates.
- Cache volume: investigate expiry and lookup changes before adjusting thresholds.
- Evaluation process: freeze one KB version per run and report versions separately.
- Quality gates: replace tutorial defaults with justified regression thresholds.
- Reporting: use N/A for unavailable features and label metric definitions accurately.

Change one factor at a time and rerun the evaluation. Higher top-k can improve
coverage while increasing irrelevant context, latency and cost.

## 3. Defensible thresholds

These are provisional quality targets, not measured baselines or course requirements:

| Metric | Provisional target |
|---|---:|
| Faithfulness | ≥ 0.85 |
| Answer relevance | ≥ 0.80 |
| Context precision | ≥ 0.75 |
| Context recall | ≥ 0.80 |

Final regression thresholds should use repeated runs on a fixed golden set and
unchanged KB version, with the judge model and evaluation-library version recorded.
Allow tolerances based on observed scoring variation. Review unsupported-answer
cases separately; do not lower thresholds merely to accept a poor baseline.
Investigate cache-hit accuracy below cache-miss accuracy, accounting for sample
size and question difficulty.

## 4. DR #2 statement

Sam's report does not demonstrate M2 readiness. First, repeat the evaluation on
one unchanged KB version so the results are interpretable and reproducible.
Second, investigate and correct unsupported answers, including possible stale
or incorrectly matched cached responses, because confident misinformation
undermines trust. Missing multi-hop evidence and irrelevant retrieved passages
also require targeted experiments. Passing thresholds of 0.30 and reporting
acceptable cost do not establish quality. Reassess readiness using justified
gates, reviewed failure cases and accurately labelled KPIs.