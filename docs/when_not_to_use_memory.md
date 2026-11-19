# Week 15 — Memory-Honesty Drill
## Results
## Comparison Interpretation
## Proposed BrightPath Decision
## Verification

| ID | Kind | Effect | Why |
|---|---|---|---|
| Q1 | Preference | Helps | Remembered bullet-point preference produces the requested format. |
| Q2 | Preference | Helps | Remembered presentation preference personalizes the response correctly. |
| Q3 | Stateless | Neutral | Arithmetic is correct without user memory. |
| Q4 | Stateless | Neutral | Counting HR documents does not require personal memory. |
| Q5 | Stateless | Neutral | The notice-period question is answered correctly in both modes. |
| Q6 | Stateless | Neutral | Time conversion does not require personal memory. |
| Q7 | Stateless | Neutral | Expanding PTO does not require personal memory. |
| Q8 | Stale | Hurts | An outdated project assignment causes an incorrect answer. |
| Q9 | Stale | Hurts | An outdated office assignment causes an incorrect answer. |


Comparison interpretation
On the supplied offline benchmark, memory ON and OFF both achieved 7/9 correct answers, so memory provided no overall correctness improvement. Memory increased the average prompt-character cost proxy by approximately 47%. It helped stable formatting preferences but harmed answers involving stale project and office assignments.

Proposed BrightPath decision
I propose limited memory for explicitly requested, stable preferences such as response format, while retrieving current policy facts from the knowledge base. The capstone’s repeat-user rate has not been measured, so there is insufficient evidence to justify broader persistent memory. I would avoid storing employee identifiers, medical details, or other sensitive personal information and provide TTL and user-controlled forgetting.

All nine questions graded correctly after correcting my initial classifications. Q1–Q2 help, Q3–Q7 are neutral, and Q8–Q9 hurt. Results come from the deterministic offline mock; prompt characters are a cost proxy, not measured API spending.

Comparison evidence: eval/logs/wk15-memory-comparison.txt