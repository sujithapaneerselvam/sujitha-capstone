# Week 12 — RAG Debugging Drill


## Scope

I inspected six synthetic pipeline traces from Week 12 Notebook 1.
All six classifications passed the notebook grader. The fixes below are
proposed actions; they have not been implemented in my live capstone.

## Diagnosis table

| Scenario | Symptom | Bucket | Trace evidence | Root cause | Smallest proposed fix |
|---|---|---|---|---|---|
| S1 | Remote-work answer omits the meetings requirement | Retrieval | Only g015-a is retrieved; the second-hop passage is absent and distractors fill the remaining slots | Recall failure | Test query expansion or increased top-k so both required passages reach the context |
| S2 | BYOD question receives an office-kitchen answer | Retrieval | All top-three results are unrelated kb-* passages, and reranking keeps them | Precision/ranking failure | Test retrieval weighting or reranking changes to promote relevant passages |
| S3 | Answer invents a 150%-of-salary cash-out benefit | Generation | Relevant g001-a and g001-b passages are present and grounding is enabled, but the answer adds an unsupported claim | Unsupported generation | Tighten grounding instructions and check claims against context before returning the answer |
| S4 | Security-incident answer adds public Slack reporting | Prompt | has_grounding_instruction is false | Missing context-only instruction | Restore the grounding instruction in the prompt template |
| S5 | Work-from-home question receives working-hours answer | Infra | Cache returns an answer cached for g003; retrieval and generation are skipped | Incorrect cache match or stale entry | Correct cache matching and invalidate affected entries after KB changes |
| S6 | Request returns no answer after a long delay | Infra | Generate fails after 30,000 ms with retries=0 | Model/API timeout without retry handling | Add bounded retries with backoff and a total timeout budget |

## Classification results

- S1: retrieval — passed
- S2: retrieval — passed
- S3: generation — passed
- S4: prompt — passed
- S5: infra — passed
- S6: infra — passed

Result: 6/6 classifications correct.

## Verification plan

- S1: Confirm both required passages are retrieved and the answer covers both
  parts of the question.
- S2: Confirm relevant passages outrank distractors and the answer addresses BYOD.
- S3: Confirm every policy claim is supported and the invented cash-out claim
  is absent.
- S4: Confirm the rendered prompt contains the grounding instruction and the
  answer does not add unsupported reporting steps.
- S5: Confirm unrelated questions cannot reuse each other's cached answers and
  KB updates invalidate affected entries.
- S6: Simulate timeouts and confirm bounded retries, a controlled failure
  response and compliance with the total timeout budget.

After each change, rerun the full evaluation suite to check for regressions.
Increasing top-k can improve recall while increasing noise, context size and cost.

## Lessons learned

I should identify the first incorrect pipeline stage before choosing a fix.
Missing evidence is a retrieval problem, while unsupported claims despite
sufficient evidence indicate a generation problem. A missing grounding
instruction is a prompt problem. Cache mismatches and model-call timeouts
belong to the infra bucket used by this exercise.

The notebook's latency and cost values are synthetic demonstration values,
not measurements of my capstone.