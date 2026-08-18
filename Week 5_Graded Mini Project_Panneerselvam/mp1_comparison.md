# MP1 Prompt Strategy Comparison

All four strategies used gpt-4o-mini at temperature 0.0. Each was scored on the same 10 job postings.

| Strategy   | Accuracy   | Parse rate   | LLM judge   | Total cost   | Latency p50   |   Successful calls |
|:-----------|:-----------|:-------------|:------------|:-------------|:--------------|-------------------:|
| zero_shot  | 2.90 / 3   | 100%         | 4.00 / 4    | USD 0.007004 | 2.608s        |                 10 |
| few_shot   | 3.00 / 3   | 100%         | 4.00 / 4    | USD 0.007254 | 3.713s        |                 10 |
| structured | 2.90 / 3   | 100%         | 4.00 / 4    | USD 0.007231 | 4.857s        |                 10 |
| cot        | 2.70 / 3   | 100%         | 3.90 / 4    | USD 0.007330 | 5.910s        |                 10 |

## J10 null-value check

J10 does not state years of experience. The correct value is null; any number is a hallucination.

- zero_shot: years = None, accuracy = 3/3, judge = 4/4.
- few_shot: years = None, accuracy = 3/3, judge = 4/4.
- structured: years = None, accuracy = 3/3, judge = 4/4.
- cot: years = None, accuracy = 3/3, judge = 4/4.
