# Data Acquisition & Verification Runbook

## Purpose
This runbook provides the standard local execution path for validating data acquisition artifacts.

## Prerequisites
- Python 3.10+ installed
- Working directory set to repository root

## Execution
Run:

```powershell
python .\tests\run_validation.py
python .\tests\validate_schema.py
```

### Live Evidence Bundle (one command)
Run:

```powershell
python .\tests\run_live_evidence.py
```

This command performs live API pulls (USGS, NOAA, FEMA), writes raw payloads, generates structured validated output, runs schema validation, and emits evidence reports.

## Expected Console Output
- File write confirmation for:
  - `tests/test-results.json`
  - `tests/test-results.md`
- Final status line:
  - `Overall: PASS`

## Artifacts Produced
- `data/sample-validated-output.json` (pipeline-generated structured output)
- `tests/test-results.md` (human-readable summary)
- `tests/test-results.json` (machine-readable result object)
- `logs/run-manifest.jsonl` (append-only run manifests)
- `logs/dead-letter.jsonl` (invalid record captures when present)
- `data/live/raw/<run_id>/` (live source payload snapshots)
- `data/live/validated-output-<run_id>.json` (live verified output)
- `logs/live-fetch-log.jsonl` (live fetch telemetry logs)
- `tests/live-test-results-<run_id>.md` (live run evidence summary)

## Troubleshooting
- If Python is not found, use your full Python path.
- If output reports `FAIL`, open `tests/test-results.md` and review failing check notes.
- If paths fail, confirm you are running from repository root.

## Quality Target
This component is considered execution-ready when validation returns `Overall: PASS` and all required artifacts are present.
