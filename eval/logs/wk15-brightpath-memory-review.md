# Week 15 — BrightPath Memory Review

AI-assisted review of 40 saved live runs against 12 supplied fictional academic policies. No new model calls. Confirm this review before submission. Raw results were preserved.

## Scoring rules

- **fact_correct**: Core requested facts complete and correct; omissions fail. Correct abstention passes without requiring optional routing advice.
- **grounded**: Substantive policy assertions supported in full supplied corpus; not proof of support in exact retrieved chunks. Incompleteness is separate.
- **citation_valid**: Strict source-level precision: explicitly attributed/listed sources must support associated claim; numeric markers optional. Exact chunk marker mapping unavailable.
- **preference_met**: Substantive answer uses bullet-list presentation, including prose lead-in plus list. Same target applied to OFF and ON.

Grounding here is corpus-level support, not live RAGAS or claim support in the exact retrieved chunks. Citation score measures source precision, not numeric-marker formatting. All fields are scored; no unresolved entries.

## Results

| Measure | Memory OFF | Memory ON |
|---|---:|---:|
| Complete factual correctness | 13/20 (65%) | 13/20 (65%) |
| Corpus-grounded policy claims | 17/20 (85%) | 18/20 (90%) |
| Precise source attribution | 12/20 (60%) | 14/20 (70%) |
| Bullet-format adherence | 5/20 (25%) | 20/20 (100%) |
| Policy execution success | 20/20 (100%) | 20/20 (100%) |
| Mean outer-agent prompt characters | 1,665.8 | 1,957.1 |
| Latency P50 (ms) | 9,060.5 | 9,942.5 |
| Latency P95 (ms) | 11,257.0 | 12,140.6 |
| Actual API cost | Unmeasured | Unmeasured |

Percentiles use linear interpolation at (n-1)*p. These are single-sample-per-question observations; no causal latency claim. Prompt characters exclude downstream policy service calls.

## Paired findings

Factual completeness is unchanged: 13/20 in both modes. Failures q08–q13 and q15 recur with memory ON and OFF. Bullet adherence increases from 5/20 to 20/20, while mean outer-agent prompt characters increase by 17.5%. Differences in grounding and citation counts reflect generated wording/source choices, not proven causal effects of memory.

## Reference caveats

- q09: account activation, MFA and equipment acknowledgement are explicitly first-day steps. VPN installation/testing are in the VPN guide, but the corpus does not explicitly assign every VPN step a first-day deadline. Both answers still miss the explicit onboarding steps.
- q14: core sick-leave reclassification and evidence deadline are correct. Emergency guidance in the golden answer applies conditionally; the question does not explicitly state an emergency. Both modes pass this interpretation.
- q17–q20: correct abstention on missing numeric limits is sufficient for fact correctness. Suggested support routing is assessed as advice, with precision caveats in per-row notes.
- Numeric [n] marker validation is not claimed: tool observations contain filenames/scores without stable chunk identifiers or an explicit marker map.

## Per-question review

F = factual completeness, G = corpus grounding, C = source precision, P = bullet preference.

| ID | OFF F/G/C/P | ON F/G/C/P | Evidence and rationale |
|---|---|---|---|
| q01 | pass/pass/pass/fail | pass/pass/pass/pass | Correct annual entitlement. Evidence: HR_02_Annual_Leave_Policy.txt. |
| q02 | pass/pass/pass/fail | pass/pass/pass/pass | Correct notice period. Evidence: HR_02_Annual_Leave_Policy.txt. |
| q03 | pass/pass/fail/fail | pass/pass/fail/pass | Fact correct. Onboarding guide is also listed/attributed but its 10 a.m. orientation does not support the remote collaboration-hours claim. Evidence: HR_03_Remote_Work_Policy.txt. |
| q04 | pass/pass/pass/pass | pass/pass/pass/pass | Correct dependant categories. Evidence: HR_04_Employee_Benefits_Guide.txt. |
| q05 | pass/pass/pass/fail | pass/pass/pass/pass | Correct flight class. Evidence: HR_05_Travel_and_Expense_Policy.txt. |
| q06 | pass/pass/pass/fail | pass/pass/pass/pass | Correct minimum length. Evidence: IT_01_Password_and_MFA_Guide.txt. |
| q07 | pass/pass/fail/fail | pass/pass/fail/pass | Download location and prohibited sources are correct. Remote Work Policy is additionally attributed but does not state the prohibited-download rule; source precision fails. Evidence: IT_02_VPN_Setup_Guide.txt. |
| q08 | fail/fail/fail/fail | fail/fail/fail/pass | Incorrect first-contact route. Onboarding example concerns a laptop not yet delivered, not a missing assigned device. Evidence: IT_06_Lost_or_Stolen_Device_Procedure.txt. |
| q09 | fail/fail/fail/fail | fail/pass/fail/pass | Unnecessary abstention: onboarding provides account activation/MFA/equipment steps. VPN guide provides install/sign-in/MFA/connection verification; exact first-day deadline for VPN is not explicit in corpus. Evidence: HR_01_Employee_Onboarding_Guide.txt. |
| q10 | fail/pass/fail/pass | fail/pass/fail/pass | Incomplete: omits managed/compliant device and MFA. Stated network/VPN precautions are supported, but verify-network/disable-auto-connect are misattributed to Laptop Policy (they occur in VPN Guide). Evidence: IT_02_VPN_Setup_Guide.txt. |
| q11 | fail/pass/pass/fail | fail/pass/pass/pass | Incomplete: revoke old MFA and immediate report are supported, but explicit security hotline, trusted-device password reset and denying unexpected prompts are omitted. Evidence: IT_06_Lost_or_Stolen_Device_Procedure.txt. |
| q12 | fail/pass/fail/pass | fail/pass/pass/pass | Incomplete: does not explicitly identify application-owner approval and least privilege; required permission/business request details are missing. Evidence: IT_04_Software_Access_Request_Process.txt. |
| q13 | fail/pass/fail/pass | fail/pass/pass/pass | Incomplete: physical protections are correct but internal-access controls (managed device, public-network verification, VPN) are missing. Evidence: IT_03_Laptop_and_Equipment_Policy.txt. |
| q14 | pass/pass/pass/fail | pass/pass/pass/pass | Core question answered correctly. Golden reference adds conditional emergency steps; question does not explicitly state an emergency, so omission alone is not failed. Evidence: HR_02_Annual_Leave_Policy.txt. |
| q15 | fail/fail/fail/pass | fail/fail/fail/pass | Incorrect/incomplete return guidance: asset remaining assigned until receipt is converted into keeping physical equipment until receipt; omits return deadline and no-deletion/personal-copy restriction. Access-removal guidance is correct. Evidence: IT_03_Laptop_and_Equipment_Policy.txt. |
| q16 | pass/pass/pass/fail | pass/pass/pass/pass | Correct decline/report response during active supplier selection. Evidence: HR_06_Code_of_Conduct.txt. |
| q17 | pass/pass/pass/fail | pass/pass/pass/pass | Correctly avoids inventing a Chennai amount: corpus contains no numeric city table. Escalation differs from Finance Help in reference; suggestions are advice, not scored as binding policy facts. Evidence: HR_05_Travel_and_Expense_Policy.txt. |
| q18 | pass/pass/pass/fail | pass/pass/pass/pass | Correctly rejects a numeric no-approval allowance; written approvals required. No invented day count. Evidence: HR_03_Remote_Work_Policy.txt. |
| q19 | pass/pass/pass/fail | pass/pass/pass/pass | Correctly avoids inventing a fee; no employee liability amount specified. Dollar wording unnecessarily assumes currency; manager/HR suggestions are less precise than IT Asset Management, but labelled suggestions. Evidence: IT_03_Laptop_and_Equipment_Policy.txt. |
| q20 | pass/pass/pass/fail | pass/pass/pass/pass | Correctly abstains on exact coverage amount; numeric limit absent. Suggested benefits portal is appropriate. Evidence: HR_04_Employee_Benefits_Guide.txt. |

## Proposed ADR entry

**Decision: limited, opt-in presentation memory; broader memory disabled.** Persist only preferred_format (bullets/prose), with 30-day TTL and user forgetting. Retrieve current policy facts from Qdrant; never treat stored preferences as policy evidence.

On this 20-question live set, bullet preference adherence improved from 25% to 100%, but complete factual correctness remained 65% in both modes, and prompt-character proxy rose 17.5%. Memory does not remedy retrieval/answer-completeness problems. Repeat-user rate and actual API cost remain unmeasured; this supports a limited experiment, not unconditional production adoption.

Priorities: fix q08 routing and q09 retrieval; complete multi-document answers q10–q13/q15; repair source attribution; retain failed cases as regressions. Do not rerun paid comparisons solely to seek higher scores.

## Provenance

- Pasted text(20261123-134309).txt: SHA-256 b25845638aa261a2c20a706d37d83de947d63eb25fec387b2774e66306fd5908
- brightpath-review-corpus.zip: SHA-256 ed0e2019d0f1e46bf382f3c651304d4a72c6c2b7381eb51e9fb70002e146d472
