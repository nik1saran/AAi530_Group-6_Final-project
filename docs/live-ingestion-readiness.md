# Live Ingestion Readiness Notes

## Current Implementation
- HTTP connector module implemented: `src/crisis/connectors.py`
- Retry with exponential backoff implemented.
- Source catalog endpoints centralized in `src/crisis/source_catalog.py`.
- Source fetch errors are captured per source (for source-health monitoring).
- One-command live evidence runner: `tests/run_live_evidence.py`

## Secrets and Configuration
- Current listed sources are public endpoints and do not require credentials.
- If authenticated APIs are added, use environment variables and never hardcode secrets.
- Recommended secret keys:
  - `CRISIS_API_KEY_<SOURCE>`
  - `CRISIS_TIMEOUT_SECONDS`
  - `CRISIS_MAX_RETRIES`

## Reliability Controls
- Retry and backoff in connector.
- Fallback to Tier B/Tier C status ceilings when Tier A unavailable.
- Run-manifest for deterministic replay evidence.
- Dead-letter file for malformed records.
- Live fetch telemetry log with latency and status:
  - `logs/live-fetch-log.jsonl`

## Next Production Steps
1. Add provider-specific adapters with pagination/checkpoint support.
2. Add source uptime and latency metrics.
3. Add connector-level unit tests with mocked HTTP failures.
4. Add per-source rate-limit policy table.
