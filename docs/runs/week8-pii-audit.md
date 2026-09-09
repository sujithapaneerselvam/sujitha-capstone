

# Week 8 Evaluation Results

## Configuration

- Qdrant collection: `capstone_chunks_v2`
- Embedding model: `text-embedding-3-small`
- Retrieval top-k: 10
- Files ingested: 12
- Total chunks: 313
- Evaluation run ID: `1788945108`

## Evaluation metrics

| Metric | Result |
| --- | ---: |
| Questions evaluated | 20 |
| Retrieval hits | 16/20 |
| Reported hit rate | 80% |
| Questions with expected sources | 16 |
| Expected-source hits | 16/16 |
| Average latency | 2263.48 ms |
| Total recorded cost | $0.003286 |
| Average recorded cost per question | $0.000164 |

## Interpretation

The Week 8 collection retrieved at least one expected source for all 16
questions that define an `expected_source`.

Questions Q17–Q20 intentionally have empty expected-source lists because they
test how the application handles information that is not available in the
corpus. The current evaluation logic records these questions as `hit=0`.
Therefore, the overall reported result is 16/20, while retrieval accuracy
among eligible expected-source questions is 16/16.

The recorded cost is the cost reported by the answer-generation pipeline.
It may not include the cost of creating embeddings during ingestion or query
embedding generation.


## Before-and-after results

| Measurement | Initial configuration | Corrected configuration |
| --- | ---: | ---: |
| Total chunks | 313 | 313 |
| Chunks with PII detection flags | 52 | 0 |
| Total detector events | 103 | 0 |

The initial Presidio configuration enabled a broad set of entity types.
This produced many false-positive detections. Policy facts such as
annual-leave durations, accrual rates, deadlines, dates, and country names
were incorrectly replaced with `<DATE_TIME>` and `<LOCATION>`.

The Presidio allowlist was restricted to:

- `PERSON`
- `EMAIL_ADDRESS`
- `PHONE_NUMBER`
- `IBAN_CODE`
- `CREDIT_CARD`

The phone-number regular expression was also improved so that complete phone
numbers are replaced instead of leaving partial digits.

After rebuilding `capstone_chunks_v2`, all 313 corpus chunks contained zero
detection events. A reproducible manual audit of 10 sampled chunks also found
no visible PII.

Zero detected items does not prove that the complete corpus contains no PII.
It means that no values matching the configured regular expressions and
Presidio entities were detected. Manual auditing and adversarial testing
remain necessary.

## Synthetic PII test

A synthetic test containing a person's name, email address, and phone number
successfully detected and scrubbed the following entity types:

- `PERSON`
- `EMAIL`
- `PHONE`

The phone number was completely removed after improving the regular
expression.

Presidio slightly overextended the `PERSON` span in the sentence
“Alice Johnson can be contacted,” producing output similar to
`<PERSON>be contacted`.

This shows that named-entity recognition boundaries can be imperfect even
when the sensitive value is successfully removed. This boundary behaviour is
recorded as a known limitation.