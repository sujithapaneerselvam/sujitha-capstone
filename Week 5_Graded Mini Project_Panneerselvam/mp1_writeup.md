# MP1 Reflection — Prompt Strategy Comparison

## Which strategy performed best?

The **zero_shot** strategy performed best in this run, with an accuracy of 0.00/3, a parse rate of 0%, and an LLM-as-a-judge score of 1.00/4. I selected the winner by considering field-level accuracy first, then parse reliability and judge quality. This ordering matters because an extraction system is useful only when it returns the correct values in a form that a downstream program can consume reliably. Cost and latency were also recorded so that the recommendation is not based on output quality alone.

## What surprised me?

All four strategies preserved the null value in J10, showing that the explicit null instruction was effective. This reinforced that a response can sound helpful to a person but still be unsuitable for an application when it is not valid JSON or when a required field has the wrong type. The J10 case is particularly important: the job posting does not state a minimum experience requirement, so null is the correct answer. Returning a plausible number would look complete, but it would be a hallucination and would reduce trust in the system.

## Which strategy would I use for my capstone?

For my Enterprise Knowledge Assistant capstone, I would start with the structured / role-based strategy. The capstone needs consistent fields, citations, confidence, and clear escalation behaviour, so an explicit output contract is safer than a loose conversational prompt. I would retain a small number of relevant few-shot examples if they improve difficult cases, but I would keep the output instructions simple and validate every response before displaying it to a user.

## What would I try next?

With another day, I would add more ambiguous examples, analyse accuracy separately for each field, and run the judge multiple times to measure judge variance. I would also compare a schema-only prompt with the winning strategy before adopting it for the capstone. Finally, I would create targeted tests for missing experience values, ranges such as 3–5 years, and expressions such as 5+ years. Those tests would make the evaluation more representative of the imperfect language that a real knowledge assistant must handle.
