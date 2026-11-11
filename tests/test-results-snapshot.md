# Validation Snapshot

## Snapshot Summary
- **Input:** `tests\fixtures\input-claims.json`
- **Output:** `data\sample-validated-output.json`
- **Records evaluated:** 6
- **Overall:** PASS

## Check Results

| Check ID | Check | Status |
|---|---|---|
| QG-01 | Attribution coverage | PASS |
| QG-02 | No unsupported confirmations | PASS |
| QG-03 | Conflict transparency | PASS |
| QG-04 | Freshness precedence | PASS |
| QG-05 | Deterministic outputs | PASS |
| QG-06 | Status and confidence validity | PASS |

## Notes
This snapshot is a fixed evidence artifact for documentation/presentation.  
Current run outputs should always be taken from:
- `tests/test-results.md`
- `tests/test-results.json`
