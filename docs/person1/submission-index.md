# Person 1 Submission Index

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Scope
Person 1 deliverable covers **Data Acquisition & Verification** only:
- Source selection and ingestion
- Verification classification (`confirmed`, `preliminary`, `unverified`)
- Conflict detection and attribution integrity
- Structured output for downstream components

## Core Documents

1. **Verification Policy**  
   `docs/person1/verification-policy.md`

2. **Data Schema Specification**  
   `docs/person1/data-schema.md`

3. **Decision Logic Specification**  
   `docs/person1/decision-logic.md`

4. **Data Source Strategy (HTML)**  
   `Person 1 - Data Sources, Validation, and Source-of-Truth Strategy.html`

5. **Execution Checklist (HTML)**  
   `Person 1 - Data Acquisition & Verification Checklist.html`

6. **Runbook**  
   `docs/person1/runbook.md`

7. **Assumptions Register**  
   `docs/person1/assumptions-register.md`

8. **Threat Model**  
   `docs/person1/threat-model.md`

9. **Source Compliance and Scope**  
   `docs/person1/source-compliance-and-scope.md`

10. **Hardening Coverage Matrix**  
    `docs/person1/hardening-coverage-matrix.md`

11. **Live Ingestion Readiness**  
    `docs/person1/live-ingestion-readiness.md`

## Test & Validation Artifacts

1. **Test Matrix**  
   `tests/person1/test-matrix.md`

2. **Validation Runner**  
   `tests/person1/run_validation.py`

3. **Schema Validator**  
   `tests/person1/validate_schema.py`

4. **Validation Results (Human-readable)**  
   `tests/person1/test-results.md`

5. **Validation Results (Machine-readable)**  
   `tests/person1/test-results.json`

6. **Sample Validated Output**  
   `data/person1/sample-validated-output.json`

7. **Validation Snapshot (Fixed Evidence)**  
   `tests/person1/test-results-snapshot.md`

8. **Fixture Input Dataset**  
   `tests/person1/fixtures/input-claims.json`

9. **Run Manifest Log**  
   `logs/person1/run-manifest.jsonl`

## Implementation Artifacts

1. **Pipeline Package**  
   `src/person1/`

2. **Machine Schema**  
   `schemas/person1/verified-crisis-batch.schema.json`

3. **CI Validation Workflow**  
   `.github/workflows/person1-validation.yml`

4. **Live Connectors**  
   `src/person1/connectors.py`

## Presentation Artifacts

1. **Data Flow Diagram (SVG)**  
   `assets/person1/person1-data-flow.svg`

2. **Data Source Strategy (PDF Export)**  
   `assets/person1/person1-data-sources-strategy.pdf`

3. **Checklist (PDF Export)**  
   `assets/person1/person1-checklist.pdf`

4. **Optional Notebook Walkthrough**  
   `notebooks/person1-validation-walkthrough.ipynb`

## Current Status
- Policy and schema definitions: complete
- Deterministic verification logic specification: complete
- Test matrix and execution artifacts: complete
- Validation run: complete (`PASS`)

## Usage Notes
- Re-run validation from repo root:
  - `python .\tests\person1\run_validation.py`
- Validation output files are overwritten on each run.

## Handoff Contract (for Person 2+)
Downstream components should consume:
- `data/person1/sample-validated-output.json` (schema-conformant shape)
- `docs/person1/data-schema.md` for field semantics
- `docs/person1/decision-logic.md` for status/confidence interpretation
