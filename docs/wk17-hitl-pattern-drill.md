## Part 1 — Gate decisions
| Action | AUTO / GATE | Primary pattern | Why |
|---|---|---|---|
| `search_web(query)` | AUTO | Reversible vs. irreversible | An ordinary public-information lookup can run without the user approving each search. |
| `send_email(to, body)` | GATE | Approval gate | The recipient may read or forward the message immediately. Show the recipient and body before sending. |
| `query_sql` (read-only `SELECT`) | AUTO | Reversible vs. irreversible | An authorized read does not change database records. |
| `delete_record(id)` | GATE | Approval gate | Deleting the wrong record can cause data loss; show the exact record before execution. |
| `charge_card(amount)` | GATE | Approval gate | A charge moves money; a later refund is a separate transaction. |
| Answer at 55% confidence | GATE | Confidence threshold | For this drill, I treat 55% as below the threshold for an automatic answer, so the agent asks for clarification or review. |
| Request outside the agent’s scope | GATE | Escalation | Stop the automated answer and hand the request to an appropriate human. Approval alone does not expand the agent’s scope. |
## Part 2 — Audit fields
## Demo verification

I ran the reconstructed BrightPath demo in Vocareum. Before a simulated
email could be sent, the UI showed the recipient and exact message for
review. I approved one request and rejected a second. Both decisions
appeared in the audit trail, and no requests remained pending.

[Pending approval](wk17-evidence/01-pending-approval.png) ·
[Recorded decisions](wk17-evidence/02-audit-decisions.png)

For every approval decision, record five fields:
| Field | Purpose |
|---|---|
| `ts` | When the reviewer made the decision. |
| `user` | Who approved or rejected the action. |
| `tool` | Which action was proposed, such as `send_email`. |
| `args` | What the reviewer was asked to authorize, such as the recipient and a redacted message summary or draft reference. |
| `decision` | Whether the reviewer selected `approve` or `reject`. |
Together, these fields let a reviewer reconstruct who decided what, and when, including requests that were rejected. The database can also have an id as its primary key; that is separate from the five audit fields. An approve entry records authorization; it does not by itself prove delivery.

## Part 3 — BrightPath gate decision
BrightPath should run lookup_policy automatically because it only reads policy information. It should put send_email behind an approval gate because a delivered email cannot reliably be recalled. The reviewer sees the recipient and draft before deciding: Approve permits the mock send; Reject cancels it. The audit trail records either decision. A human makes the final call because even a correct policy summary can be sent to the wrong person.
## Planner and reflection — offline verification

The BrightPath graph retried the annual-leave lookup once when the first
answer lacked a citation. When the retry supplied a citation, the graph
returned both the entitlement and advance-notice answers with their source.
When the retry also lacked a citation, the graph abstained on entitlement
and still returned the supported advance-notice answer.

Verification: `python3 -m pytest -q tests/test_wk16_graph.py tests/test_wk17_graph.py`
Result: 7 passed. The policy lookup was mocked; no live API calls were made.