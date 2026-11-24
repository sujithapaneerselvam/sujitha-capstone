## Offline Activity — Memory-Honesty Drill

| ID | Kind | ON correct | OFF correct | Effect | Why |
|---|---|---|---|---|---|
| Q1 | Preference | Yes | No | Helps | Remembers the requested bullet format. |
| Q2 | Preference | Yes | No | Helps | Applies the user's preferred presentation. |
| Q3 | Stateless | Yes | Yes | Neutral | Arithmetic needs no personal memory. |
| Q4 | Stateless | Yes | Yes | Neutral | Document counting needs no personal memory. |
| Q5 | Stateless | Yes | Yes | Neutral | Both modes answer the policy question correctly. |
| Q6 | Stateless | Yes | Yes | Neutral | Time conversion needs no personal memory. |
| Q7 | Stateless | Yes | Yes | Neutral | Acronym expansion needs no personal memory. |
| Q8 | Stale | No | Yes | Hurts | Uses an outdated project assignment. |
| Q9 | Stale | No | Yes | Hurts | Uses an outdated office assignment. |

### Comparison Interpretation

Both modes achieved 7/9 correct answers (77.8%), so memory provided
no overall correctness improvement. Memory increased the overall
prompt-character cost proxy by approximately 47%, helped two preference
questions, hurt two stale-context questions, and was neutral on five.

This was a deterministic offline mock, not a live accuracy benchmark
or measured API spending. All nine classifications passed the grader.

### Proposed BrightPath Decision

Use limited, opt-in memory for stable formatting preferences.
Retrieve changing policy facts from the knowledge base rather than
user memory. Repeat-user rate is unmeasured; avoid persisting sensitive
employee details and provide TTL and user-controlled forgetting.

Evidence: eval/logs/wk15-memory-comparison.txt


## BrightPath Capstone — Live Memory Smoke Test

In a live two-question comparison, memory ON and OFF both produced
correct policy facts (2/2 per mode), and all four policy lookups
succeeded. Memory ON applied the stored bullet-format preference;
memory OFF used prose and requested the preference in one response.

Source filenames appeared in all four answers, but memory ON omitted
the numbered citation markers. Citation formatting needs further review.

This small smoke test supports limited preference memory but does not
establish a general quality or latency improvement. The first OFF
request took 165.7 seconds; startup or warm-up may have contributed.
Actual API cost was not measured.

Evidence: eval/logs/wk15-brightpath-memory-smoke.json

Status: The smoke test, 40 live runs, and AI-assisted corpus review
are complete. I checked the AI-assisted scoring notes against the existing corpus
and confirmed the results. The corpus was not changed.
Answer-completeness and citation issues remain documented follow-up work.

## BrightPath Capstone — Full 20-Question Comparison
All 40 runs completed, with 20/20 successful policy calls in each mode. Memory ON consistently applied bullet formatting and increased the mean outer-agent prompt-character proxy by 17.5%. Policy-answer problems appeared in both modes, including disagreement with the reference for q08 and an unnecessary abstention for q09. Factual correctness and grounding remain under review; actual API cost was not measured.

## Completion Status

All nine offline drill classifications passed.
The BrightPath memory implementation, 40 live runs, and AI-assisted
corpus review are complete.
I checked the AI-assisted scoring notes against the existing corpus
and confirmed the results. The corpus was not changed.
Answer-completeness and citation issues remain documented follow-up work.