# Person 1 Hardening Coverage Matrix

This matrix maps previously identified risk/fault themes to implemented controls.

| Control Theme | Implemented Artifact(s) | Status |
|---|---|---|
| Executable ingestion/verification pipeline | `src/person1/pipeline.py`, `src/person1/verification.py` | Implemented |
| Deterministic normalization and dedup | `src/person1/normalization.py` | Implemented |
| Source hierarchy and catalog governance | `src/person1/source_catalog.py`, `docs/person1/verification-policy.md` | Implemented |
| Field-level schema contract | `schemas/person1/verified-crisis-batch.schema.json`, `tests/person1/validate_schema.py` | Implemented |
| Conflict detection with explicit details | `src/person1/verification.py` | Implemented |
| Supersession and freshness precedence | `src/person1/verification.py`, `tests/person1/run_validation.py` | Implemented |
| Confidence scoring model | `src/person1/config.py`, `src/person1/verification.py` | Implemented |
| Unsupported confirmation prevention | `tests/person1/run_validation.py` (QG-02) | Implemented |
| Timestamp ordering validation | `tests/person1/run_validation.py` (QG-06) | Implemented |
| Repeatable run traceability | `logs/person1/run-manifest.jsonl`, `src/person1/audit.py` | Implemented |
| Invalid record quarantine | `logs/person1/dead-letter.jsonl`, `src/person1/pipeline.py` | Implemented |
| Fixed fixture-based test scenarios | `tests/person1/fixtures/input-claims.json`, `tests/person1/test-matrix.md` | Implemented |
| CI merge guard | `.github/workflows/person1-validation.yml` | Implemented |
| Operational run instructions | `docs/person1/runbook.md` | Implemented |
| Threat model and assumptions | `docs/person1/threat-model.md`, `docs/person1/assumptions-register.md` | Implemented |
| Source compliance, scope, fallback precedence | `docs/person1/source-compliance-and-scope.md` | Implemented |

## Remaining Follow-On Enhancements
These are outside current offline fixture scope and require staged implementation with live provider integrations:
- Live connector reliability metrics (provider uptime, p95 ingestion latency)
- Production secret management and token rotation
- Full multilingual named-entity normalization pipeline
- Semantic contradiction detection beyond structured field comparisons
- Historical backfill/pagination adapters per provider API

