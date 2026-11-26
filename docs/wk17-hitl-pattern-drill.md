| Action | AUTO / GATE | Primary pattern | Why |
|---|---|---|---|
| `search_web(query)` | AUTO | Reversible vs. irreversible | An ordinary public-information lookup can run without the user approving each search. |
| `send_email(to, body)` | GATE | Approval gate | The recipient may read or forward the message immediately. Show the recipient and body before sending. |
| `query_sql` (read-only `SELECT`) | AUTO | Reversible vs. irreversible | An authorized read does not change database records. |
| `delete_record(id)` | GATE | Approval gate | Deleting the wrong record can cause data loss; show the exact record before execution. |
| `charge_card(amount)` | GATE | Approval gate | A charge moves money; a later refund is a separate transaction. |
| Answer at 55% confidence | GATE if below the configured threshold | Confidence threshold | When confidence falls below the threshold, pause for clarification or review before presenting the answer as reliable. |
| Request outside the agent’s scope | GATE / hand off | Escalation | An authorized human should handle it. Approval alone does not give BrightPath expertise outside its scope. |

## Demo verification

I ran the reconstructed BrightPath demo in Vocareum. Before a simulated
email could be sent, the UI showed the recipient and exact message for
review. I approved one request and rejected a second. Both decisions
appeared in the audit trail, and no requests remained pending.

[Pending approval](wk17-evidence/01-pending-approval.png) ·
[Recorded decisions](wk17-evidence/02-audit-decisions.png)

## Planner and reflection — offline verification

The BrightPath graph retried the annual-leave lookup once when the first
answer lacked a citation. When the retry supplied a citation, the graph
returned both the entitlement and advance-notice answers with their source.
When the retry also lacked a citation, the graph abstained on entitlement
and still returned the supported advance-notice answer.

Verification: `python3 -m pytest -q tests/test_wk16_graph.py tests/test_wk17_graph.py`
Result: 7 passed. The policy lookup was mocked; no live API calls were made.