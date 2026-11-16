# Document update runbook

Use this procedure when an existing `.txt` or `.md` policy changes.

## Before updating

1. Confirm the revised file is in `data/corpus/`.
2. Confirm `load_store()` targets `capstone_chunks_v2`.
3. Check that the source already has live chunks and the replacement
   document produces nonempty text.

## Update

From the repository root:

```bash
python3 -m scripts.update_document \
  data/corpus/HR_02_Annual_Leave_Policy.txt



# Runbook: Document Update (W10)

## Steps
1. Tombstone the old version
2. Clear the semantic cache
3. Ingest the new version
4. Bump KB_VERSION if chunking/model changed

## Verification (3 signals)
- 3a: New content reachable
- 3b: Old content gone
- 3c: Tombstones queryable for audit

## NON-NEGOTIABLE
Cache MUST be cleared on EVERY document update.
