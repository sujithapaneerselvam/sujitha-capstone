# MP1 Prompt Strategy Comparison

All four strategies used gpt-4o-mini at temperature 0.0. Each was scored on the same 10 job postings.

| Strategy   | Accuracy   | Parse rate   | LLM judge   | Total cost   | Latency p50   |   Successful calls |
|:-----------|:-----------|:-------------|:------------|:-------------|:--------------|-------------------:|
| zero_shot  | 0.00/3     | 0%           | 1.00 / 4    | USD 0.000000 | 0.000s        |                  0 |
| few_shot   | 0.00/3     | 0%           | 1.00 / 4    | USD 0.000000 | 0.000s        |                  0 |
| structured | 0.00/3     | 0%           | 1.00 / 4    | USD 0.000000 | 0.000s        |                  0 |
| cot        | 0.00/3     | 0%           | 1.00 / 4    | USD 0.000000 | 0.000s        |                  0 |

## J10 null-value check

J10 does not state years of experience. The correct value is null; any number is a hallucination.


