# Data Acquisition & Verification Submission Index

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Scope
This deliverable covers **Data Acquisition & Verification** only:
- Source selection and ingestion
- Verification classification (`confirmed`, `preliminary`, `unverified`)
- Conflict detection and attribution integrity
- Structured output for downstream components

## Core Documents

1. **Verification Policy**  
   `docs/verification-policy.md`

2. **Data Schema Specification**  
   `docs/data-schema.md`

3. **Decision Logic Specification**  
   `docs/decision-logic.md`

4. **Data Source Strategy (HTML)**  
   `Data Sources, Validation, and Source-of-Truth Strategy.html`

5. **Execution Checklist (HTML)**  
   `Data Acquisition & Verification Checklist.html`

6. **Runbook**  
   `docs/runbook.md`

7. **Assumptions Register**  
   `docs/assumptions-register.md`

8. **Threat Model**  
   `docs/threat-model.md`

9. **Source Compliance and Scope**  
   `docs/source-compliance-and-scope.md`

10. **Hardening Coverage Matrix**  
    `docs/hardening-coverage-matrix.md`

11. **Live Ingestion Readiness**  
    `docs/live-ingestion-readiness.md`

## Test & Validation Artifacts

1. **Test Matrix**  
   `tests/test-matrix.md`

2. **Validation Runner**  
   `tests/run_validation.py`

3. **Schema Validator**  
   `tests/validate_schema.py`

4. **Live Evidence Runner (One Command)**  
   `tests/run_live_evidence.py`

5. **Validation Results (Human-readable)**  
   `tests/test-results.md`

6. **Validation Results (Machine-readable)**  
   `tests/test-results.json`

7. **Sample Validated Output**  
   `data/sample-validated-output.json`

8. **Validation Snapshot (Fixed Evidence)**  
   `tests/test-results-snapshot.md`

9. **Fixture Input Dataset**  
   `tests/fixtures/input-claims.json`

10. **Run Manifest Log**  
   `logs/run-manifest.jsonl`

11. **Live Fetch Telemetry Log**  
   `logs/live-fetch-log.jsonl`

12. **Live Retrieval Evidence**  
   `docs/live-retrieval-evidence.md`

## Implementation Artifacts

1. **Pipeline Package**  
   `src/crisis/`

2. **Machine Schema**  
   `schemas/verified-crisis-batch.schema.json`

3. **CI Validation Workflow**  
   `.github/workflows/validation.yml`

4. **Live Connectors**  
   `src/crisis/connectors.py`

## Presentation Artifacts

1. **Data Flow Diagram (SVG)**  
   `assets/data-flow.svg`

2. **Data Source Strategy (PDF Export)**  
   `assets/data-sources-strategy.pdf`

3. **Checklist (PDF Export)**  
   `assets/checklist.pdf`

4. **Optional Notebook Walkthrough**  
   `notebooks/validation-walkthrough.ipynb`

## Current Status
- Policy and schema definitions: complete
- Deterministic verification logic specification: complete
- Test matrix and execution artifacts: complete
- Validation run: complete (`PASS`)

## Usage Notes
- Re-run validation from repo root:
  - `python .\tests\run_validation.py`
- Validation output files are overwritten on each run.

## Handoff Contract (for Person 2+)
Downstream components should consume:
- `data/sample-validated-output.json` (schema-conformant shape)
- `docs/data-schema.md` for field semantics
- `docs/decision-logic.md` for status/confidence interpretation
