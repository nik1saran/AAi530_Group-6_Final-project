# Person 1 Runbook

## Purpose
This runbook provides the standard local execution path for validating Person 1 artifacts.

## Prerequisites
- Python 3.10+ installed
- Working directory set to repository root

## Execution
Run:

```powershell
python .\tests\person1\run_validation.py
python .\tests\person1\validate_schema.py
```

## Expected Console Output
- File write confirmation for:
  - `tests/person1/test-results.json`
  - `tests/person1/test-results.md`
- Final status line:
  - `Overall: PASS`

## Artifacts Produced
- `data/person1/sample-validated-output.json` (pipeline-generated structured output)
- `tests/person1/test-results.md` (human-readable summary)
- `tests/person1/test-results.json` (machine-readable result object)
- `logs/person1/run-manifest.jsonl` (append-only run manifests)
- `logs/person1/dead-letter.jsonl` (invalid record captures when present)

## Troubleshooting
- If Python is not found, use your full Python path.
- If output reports `FAIL`, open `tests/person1/test-results.md` and review failing check notes.
- If paths fail, confirm you are running from repository root.

## Quality Target
Person 1 is considered execution-ready when validation returns `Overall: PASS` and all required artifacts are present.
