# ADR 0001 — Capstone Framing: Knowledge Assistant

- **Status:** Accepted
- **Date:** Week 1
- **Deciders:** <your name>

## Context
We are building a Q&A assistant over a small document corpus. The knowledge lives in
documents that can change, answers must be trustworthy, and we must be able to show where
each answer came from. We are building it one piece at a time over 30 weeks.

## Decision
We will build a **Retrieval-Augmented Generation (RAG)** system, framed by the Solution
Framing Canvas:

| Field | Choice (v1) |
|-------|-------------|
| Inputs | Document corpus + user questions |
| Tools | Retrieval + a single LLM call |
| Memory | None in v1 (added later) |
| Outputs | A grounded answer with citations |
| Autonomy | Suggest only — no destructive actions |
| Decision boundaries | Answer only from the provided documents |
| Success metrics | Grounded response · hallucination rate · task success |

## Consequences
- Fresh, private, *citable* answers without retraining a model.
- v1 is deliberately small and safe: suggest-only, answers only from our documents.
- We are *not* fine-tuning (facts change) and *not* using long-context at scale (cost).


## Week 8 decision: production-style ingestion and controlled PII scrubbing

### Context

The earlier indexing process worked for the capstone's text corpus but did
not provide a complete ingestion path for multiple document formats,
structured metadata, or auditable PII handling.

The initial Week 8 Presidio configuration used a broad entity set. It
incorrectly identified policy dates, durations, accrual rates, deadlines, and
locations as sensitive data. As a result, useful facts were replaced with
`<DATE_TIME>` and `<LOCATION>`, reducing the quality of content available for
retrieval and answer generation.

### Decision

The capstone will use the following ingestion sequence:

1. Parse supported documents.
2. Split content using recursive chunking.
3. Detect and scrub configured PII.
4. Enrich every chunk with metadata.
5. Create embeddings.
6. Upsert the chunks into Qdrant.

The Week 8 data is stored in a versioned Qdrant collection named
`capstone_chunks_v2`. The Week 7 collection is retained as a baseline and
rollback option.

The Presidio entity allowlist is restricted to:

- `PERSON`
- `EMAIL_ADDRESS`
- `PHONE_NUMBER`
- `IBAN_CODE`
- `CREDIT_CARD`

Explicit regular expressions are also used for:

- Email addresses
- Phone numbers
- Employee identifiers

Each Qdrant payload records metadata including the chunk identifier, source,
document type, section path, page, date, language, version, ingestion
timestamp, text, and PII detection count.

### Rationale

A restricted allowlist protects common personal identifiers while preserving
business-policy facts required by the RAG application. Versioning the Qdrant
collection makes comparison, rollback, and controlled migration possible.

Regular expressions provide deterministic handling for well-defined
identifiers, while Presidio provides broader named-entity detection. Neither
method is treated as complete proof that a document is free of PII.

### Consequences

#### Positive

- Important policy durations, dates, rates, and locations are preserved.
- The ingestion process supports richer metadata and multiple document
  formats.
- PII detection can be audited using the stored detection count.
- The Week 7 and Week 8 collections can be compared independently.
- The Week 8 evaluation retained 16/16 expected-source hits.

#### Limitations

- Zero detection flags does not prove that the corpus contains no PII.
- Presidio may overextend entity boundaries, as observed in the synthetic
  PERSON test.
- Some chunks contain headings without enough supporting content.
- PII configuration changes require rebuilding the collection.
- Manual audits and synthetic adversarial tests remain necessary.

### Validation

The corrected pipeline ingested 12 files and produced 313 chunks.

The initial configuration produced 103 detection events across 52 chunks,
including harmful false positives. After restricting the entity allowlist and
rebuilding the collection, the corpus produced zero detection events, and a
manual sample found no visible PII.

A synthetic test successfully detected and scrubbed PERSON, EMAIL, and PHONE
values. The Week 8 golden-set evaluation produced 16/20 reported hits, equal
to 16/16 among questions with expected sources.