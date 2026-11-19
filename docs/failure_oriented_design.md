# Week 14 — Failure-Oriented Design

## Scope

I ran the supplied Week 14 offline gauntlet through
scripts/failure_gauntlet.py, assembled from Notebook 2.

All six classifications passed. All six scenarios survived.
These results verify the sample agent, not my live BrightPath agent.

## Failure Gauntlet Results

| Scenario | Symptom | Category | Defense that saved it | Did it survive? |
|---|---|---|---|---|
| S1 | Web tool returns two rate-limit errors before succeeding | Transient | Bounded retries with backoff | Yes |
| S2 | Calculator is called without its required expression | Permanent | Schema validation and fast-fail without retry | Yes |
| S3 | Calculator receives “today plus seven days” | Silent | Arithmetic parsing and validation reject the invalid expression | Yes |
| S4 | SQL tool repeatedly times out | Cascading | Circuit breaker opens after repeated failures; agent returns a degraded response | Yes |
| S5 | Injected instruction attempts to email everyone | Adversarial | Permissioning blocks send_email before execution | Yes |
| S6 | Model repeatedly calls the calculator without finishing | Control/runaway | Maximum-iteration guard stops after five iterations | Yes |

The S3 trace reports status “ok” because the tool returned an error
message rather than raising an exception. This is not a successful
calculation; the agent recognized the invalid expression.

In S4, the final observation reports an exhausted transient failure.
The gauntlet's survival check also verifies that the SQL circuit breaker
is open.

## Circuit Breaker

In CLOSED state, calls are allowed and consecutive failures are counted;
reaching the configured failure limit changes the state to OPEN.
OPEN blocks calls until the reset timeout expires, when a trial call
is allowed in HALF_OPEN state.
A successful trial resets the failure count and returns to CLOSED;
a failed trial reopens the circuit.

The implementation is in the CircuitBreaker class in Notebook 2,
included in the generated gauntlet script.

## Permissioning

DefensePolicy.guard() checks write permissions before executing a tool:

```python
if tool_name in self.write_tools:
    return (
        f"[{tool_name} BLOCKED — requires human confirmation before a "
        f"side-effecting action]",
        "blocked",
    )
```

The send_email tool is blocked before its handler is called.
The demonstration does not send a real email or implement a complete
human-approval workflow.

## Capstone Tool Failure Profile — lookup_policy

lookup_policy calls the BrightPath policy API and returns an answer,
source metadata, and the KB version. It does not modify policies or
submit claims.

| Category | Realistic failure | Required defense |
|---|---|---|
| Transient | Temporary network failure, timeout, or rate limit | Bounded retries with backoff and a total timeout budget |
| Permanent | Blank question, invalid credentials, or invalid configuration | Input validation and fast-fail; do not repeatedly retry |
| Silent | Fluent but off-topic answer, unsupported claim, or invalid citation mapping | Validate evidence and citations; abstain when support is insufficient |
| Cascading | Repeated failures in the downstream policy service | Circuit breaker and a controlled unavailable response |
| Adversarial | Instructions request policy changes or unauthorized actions | Restricted tool capabilities and permission checks on any write tools |

The agent also needs a maximum-iteration limit.

lookup_policy is read-only at the business level, so it does not need
a write-approval workflow of its own. Repeated calls can still incur
model costs. It cannot rely on a circuit breaker to detect incorrect
policy answers; those require evidence validation.

## Current Capstone Wiring Status

Verified:
- Blank questions are rejected by the Pydantic input schema.
- The wrapper uses an HTTP timeout.
- Empty responses and known API error responses raise an exception.
- The annual-leave smoke test returned 20 days and the expected source.
- The Week 13 agent selected lookup_policy for the policy question.
- In Week 14 Notebook 2, lookup_policy calls go through DefensePolicy.guard().
- An injected timeout caused three attempts before the breaker opened.
- The agent returned a controlled unavailable response.
- A subsequent call while the breaker was open did not invoke the tool.

Implemented but not independently tested:
- The adapter maps selected HTTP and transport errors to transient
  or permanent exceptions.

Still pending for the wider capstone lab:
- Integration into the normal capstone agent entry point.
- Runtime evidence validation for unsupported policy answers.
- Five injected failure categories in my own agent, with saved traces.
- Completion of the wider lab's test suite and KPI/ADR updates.

The notebook test verifies mocked defense wiring, not live-service
failure handling.

## Verification Evidence

Commands used:

```bash
python3 scripts/failure_gauntlet.py list
python3 scripts/failure_gauntlet.py run S1
python3 scripts/failure_gauntlet.py grade S1 transient
python3 scripts/failure_gauntlet.py grade S2 permanent
python3 scripts/failure_gauntlet.py grade S3 silent
python3 scripts/failure_gauntlet.py grade S4 cascading
python3 scripts/failure_gauntlet.py grade S5 adversarial
python3 scripts/failure_gauntlet.py grade S6 control
python3 scripts/failure_gauntlet.py run-all
```

Combined results: ../../eval/logs/wk14-failure-gauntlet.txt

Offline sample-agent failure survival rate: 5/5 injected failures (100%).
The S6 control guard passed separately, stopping after five iterations.

Survival means the agent handled the injected condition without crashing
and met the scenario check. It does not mean every tool call succeeded
or every answer was correct.

[Gauntlet results](../eval/logs/wk14-failure-gauntlet.txt)