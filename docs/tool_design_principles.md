# Tool Design Principles — Week 13

A reliable tool has a clear name, a typed input schema, a scoped
model-facing description, and an explicit idempotency declaration.

## 1. Naming

Use a specific verb phrase in snake_case that describes one action.

- Good: lookup_policy, query_sql, search_web, calculate
- Avoid: data, handle, process

Split tools that perform unrelated jobs into separate tools.

## 2. Schema

Define inputs with a Pydantic model. Give every field a type, make
essential fields required, and provide defaults for optional inputs.
Validate arguments before executing the tool.

Example from my capstone:

```python
from typing import Annotated
from pydantic import BaseModel, StringConstraints


class LookupPolicyInput(BaseModel):
    question: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
```

The question is required. Empty or whitespace-only questions are rejected.
This tool currently has no optional inputs.

## 3. Description

Write the description for the model choosing the tool. Explain:

- When to use it.
- What it returns.
- When not to use it.
- Which alternative tool handles adjacent requests.

My lookup_policy description:

Use this tool to answer questions about BrightPath policy provisions,
including annual leave, remote work, benefits, and travel expenses.
It returns a policy answer and source metadata. Do not use it for
document metadata such as policy version, owner, or review date;
use query_sql for those requests. Do not use it for public facts,
calculations, submitting claims, or modifying records.

## 4. Idempotency

Declare whether repeating a call can cause additional effects.

A read-only lookup can be idempotent even if the returned wording varies.
A notification or claim-submission tool must not be retried blindly:
a timeout does not prove that the first action failed.

For tools that change state, declare the side effect and use a
deduplication or idempotency key before enabling retries.

## Capstone tool: lookup_policy

| Property | Definition |
|---|---|
| Name | lookup_policy |
| Input schema | LookupPolicyInput |
| Required input | Non-empty question string |
| Optional inputs | None |
| Output | Policy answer, citations, and KB version |
| Idempotent | True |
| Business side effects | None; does not submit claims or modify policies |

The current implementation calls the BrightPath /ask endpoint with
use_cache=false. It returns a generated answer with source metadata,
rather than raw source excerpts. It makes model calls, so repeated calls
may incur cost and produce different wording.

## Clinic verification

All six diagnoses passed:

| Case | Symptom | Principle it breaks | Why | The fix |
|---|---|---|---|---|
| C1 — The tool called `data` | The model rarely calls it, or selects it for unrelated requests. | Naming | `data` is a vague noun that does not describe the tool’s action. | Rename it to a specific verb phrase, such as `get_weather`. |
| C2 — The loose schema | Wrong or missing arguments cause runtime failures. | Schema | Untyped parameters do not tell the model what input structure is required. | Define a typed Pydantic model, mark essential fields as required, and give optional fields defaults. |
| C3 — The silent description | The model cannot distinguish when to select this tool over another. | Description | “Gets the status” does not explain when to use the tool or what it returns. | Describe its purpose, when to use it, its output, and when another tool is appropriate. |
| C4 — The unsafe retry | Retrying after a timeout sends duplicate notifications. | Idempotency | The tool sends messages but is incorrectly marked idempotent, allowing unsafe retries. | Mark it non-idempotent, document the side effect, and add a deduplication key before enabling retries. |
| C5 — The overloaded `handle` | A tool performing three jobs is selected unpredictably. | Naming | The generic name hides multiple responsibilities, making tool selection unreliable. | Split it into separate, single-purpose tools with specific verb-first names. |
| C6 — The catch-all description | The tool is selected for almost every question, crowding out better tools. | Description | Its description claims an excessively broad scope instead of stating its actual capability. | Narrow the description to its intended purpose and explicitly state when not to use it. |

The search_web, query_sql, and calculate reference tools passed all four
linter checks. They use specific action names, typed arguments, scoped
descriptions, and explicit idempotency declarations.

The clinic was executed using the equivalent cmd_list, cmd_run,
cmd_grade, and cmd_lint functions in Week 13 Notebook 1.

## Reflection

Description was the hardest principle because policy content and policy
metadata are closely related. I clarified that lookup_policy handles
policy provisions, while query_sql handles fields such as document
version. This distinction corrected the policy-version routing failure
in an observed evaluation run.