# Data Acquisition Hardening Coverage Matrix

This matrix maps previously identified risk/fault themes to implemented controls.

| Control Theme | Implemented Artifact(s) | Status |
|---|---|---|
| Executable ingestion/verification pipeline | `src/crisis/pipeline.py`, `src/crisis/verification.py` | Implemented |
| Deterministic normalization and dedup | `src/crisis/normalization.py` | Implemented |
| Source hierarchy and catalog governance | `src/crisis/source_catalog.py`, `docs/verification-policy.md` | Implemented |
| Live retrieval demonstration with logs | `tests/run_live_evidence.py`, `logs/live-fetch-log.jsonl`, `docs/live-retrieval-evidence.md` | Implemented |
| Field-level schema contract | `schemas/verified-crisis-batch.schema.json`, `tests/validate_schema.py` | Implemented |
| Conflict detection with explicit details | `src/crisis/verification.py` | Implemented |
| Supersession and freshness precedence | `src/crisis/verification.py`, `tests/run_validation.py` | Implemented |
| Confidence scoring model | `src/crisis/config.py`, `src/crisis/verification.py` | Implemented |
| Unsupported confirmation prevention | `tests/run_validation.py` (QG-02) | Implemented |
| Timestamp ordering validation | `tests/run_validation.py` (QG-06) | Implemented |
| Repeatable run traceability | `logs/run-manifest.jsonl`, `src/crisis/audit.py` | Implemented |
| Invalid record quarantine | `logs/dead-letter.jsonl`, `src/crisis/pipeline.py` | Implemented |
| Fixed fixture-based test scenarios | `tests/fixtures/input-claims.json`, `tests/test-matrix.md` | Implemented |
| CI merge guard | `.github/workflows/validation.yml` | Implemented |
| Operational run instructions | `docs/runbook.md` | Implemented |
| Threat model and assumptions | `docs/threat-model.md`, `docs/assumptions-register.md` | Implemented |
| Source compliance, scope, fallback precedence | `docs/source-compliance-and-scope.md` | Implemented |

## Remaining Follow-On Enhancements
These are outside current offline fixture scope and require staged implementation with live provider integrations:
- Live connector reliability metrics (provider uptime, p95 ingestion latency)
- Production secret management and token rotation
- Full multilingual named-entity normalization pipeline
- Semantic contradiction detection beyond structured field comparisons
- Historical backfill/pagination adapters per provider API
