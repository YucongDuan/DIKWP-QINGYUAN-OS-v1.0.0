# CLI and Output Reference

## Commands

```text
inspect
assess INPUT --output DIR
demo --output DIR
suite --examples DIR --output DIR
shield FEED --output DIR
verify LEDGER
```

## Required input fields

```json
{
  "item_id": "stable-id",
  "title": "human-readable title",
  "channel": "online | offline | hybrid",
  "text": "content or case description",
  "claims": [],
  "purpose": {"owner": "named role", "automatic_external_action_authority": 0}
}
```

See `schemas/content-item.schema.json` for the full structure.

## Determinism

Given the same normalized input and software version, the runtime produces the same `run_hash` and ledger chain. Real-world source verification and outcome measurement belong to external connectors and must be recorded as successor evidence, not silently imported into cached results.
