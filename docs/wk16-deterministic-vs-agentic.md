# Week 16 — Deterministic vs Agentic Drill

## Part 1 — Classification
| # | Concern | Type | Why |
|---|---|---|---|
| 1 | PII scrubbing | Deterministic | Redaction must be enforced before every model call; detection accuracy is tested separately. |
| 2 | Tool selection | Agentic | Selecting a suitable tool for ambiguous language requires judgment. |
| 3 | Cost cap | Deterministic | Code must consistently enforce the spending threshold. |
| 4 | Response wording/tone | Agentic | Natural-language presentation requires judgment within constraints. |
| 5 | Argument schema validation | Deterministic | Types and required fields provide explicit validation rules. |
| 6 | Retry decision | Deterministic | Error category, idempotency, and retry budget determine whether to retry. |
| 7 | Summary generation | Agentic | Combining retrieved evidence into a useful answer requires language judgment. |
| 8 | Escalation routing | Deterministic | Defined thresholds and failure signals must reliably trigger escalation. |


2. Two wrong-default examples
- If an LLM decides whether to redact detected PII, it may leave sensitive information in a request sent to an external model.
- If an LLM decides whether to obey the cost cap, it may continue making paid calls after the budget is exhausted.
3. BrightPath decision
I will use deterministic routing for policy-tool failures. In Week 15, a failed lookup led the agent to offer generic employer guidance rather than verified BrightPath policy. A failed lookup should route to a controlled unavailable response; the model should not decide whether to substitute unsupported policy facts.