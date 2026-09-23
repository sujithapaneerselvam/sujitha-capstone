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