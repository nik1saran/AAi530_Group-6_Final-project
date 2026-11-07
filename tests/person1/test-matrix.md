# Person 1 Test Matrix

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Scope
This matrix validates Person 1 outputs for data acquisition and verification quality:
- Source attribution integrity
- Status classification consistency
- Conflict detection coverage
- Freshness and supersession behavior
- Deterministic confidence scoring

## Test Execution Rules
- Use fixed input snapshots to ensure deterministic reruns.
- Log source metadata for every claim.
- Validate both expected status and expected conflict behavior.
- Record actual outcomes and pass/fail per scenario.
- Generate output through pipeline execution, not hand-authored output:
  - `python .\tests\person1\run_validation.py`
  - `python .\tests\person1\validate_schema.py`

## Scenario Matrix

| Test ID | Scenario | Input Conditions | Expected Status Outcome | Expected Conflict Behavior | Expected Confidence Band | Pass Criteria |
|---|---|---|---|---|---|---|
| P1-T01 | Single authoritative bulletin | One Tier A source with coherent event details and fresh timestamp | `confirmed` or `preliminary` (based on completeness) | No conflict flags | 0.75-0.95 | Attribution complete, no false conflicts, status aligns with policy |
| P1-T02 | Conflicting casualty counts across sources | Tier A + Tier B disagree on fatalities/injuries for same event window | `preliminary` until resolved | `conflict_casualties` and/or `conflict_injuries` flagged | 0.45-0.75 | Conflict flags present, no `confirmed` while major conflict unresolved |
| P1-T03 | Rapid update progression | Sequential updates where latest source revises impact values | Latest record active; older records superseded | No conflict if revision is traceable; otherwise timing/impact conflict flagged | 0.60-0.90 | Supersession links valid, chronology preserved, stale record marked superseded |
| P1-T04 | Uncorroborated social signal | Tier C claim with no corroboration from Tier A/B within test window | `unverified` | Optional `conflict_action_status` if contradicted by authority | 0.10-0.40 | Never classified as `confirmed`; provenance fully retained |
| P1-T05 | Stale versus fresh contradiction | Older high-impact claim conflicts with newer authoritative correction | Newer authoritative claim = active; stale claim superseded | `conflict_timing` and relevant field conflict flagged | 0.50-0.85 (new) / lower for stale | Correct precedence to fresh authoritative update |
| P1-T06 | Multi-source alignment | Tier A + independent Tier B reports agree on core facts | `confirmed` if no unresolved conflicts | No material conflict flags | 0.80-0.98 | Confirmation rule satisfied with evidence notes |
| P1-T07 | Missing attribution fields | Claim lacks source URL or retrieval timestamp | `unverified` | No automatic conflict requirement | 0.00-0.35 | Record blocked from `confirmed`; validation error surfaced |
| P1-T08 | Location mismatch for same event key | Two sources report different impacted location for same event id | `preliminary` or `unverified` | `conflict_location` flagged | 0.30-0.70 | Conflict details show both location claims with evidence links |
| P1-T09 | Partial data completeness | Authoritative source present but key impact fields are null/unknown | `preliminary` | No conflict unless contradictory values exist | 0.55-0.80 | Unknown values kept explicit; no unsupported numeric imputation |
| P1-T10 | Determinism rerun check | Re-run exact same input batch twice | Identical statuses both runs | Identical conflict flags both runs | Same confidence values | Output parity across runs with same policy version |

## Quality Gate Validation Table

| Gate ID | Quality Gate | Validation Method | Expected Result |
|---|---|---|---|
| QG-01 | 100% attribution coverage | Check non-null `source_name`, `source_url`, `retrieved_at_utc` | Pass |
| QG-02 | No unsupported confirmations | Filter records where `status=confirmed` and test evidence conditions | 0 violations |
| QG-03 | Conflict transparency | Compare known contradiction scenarios vs `conflict_flags` | All contradictions flagged |
| QG-04 | Freshness precedence | Validate supersession linkage in stale-vs-fresh tests | Correct active record precedence |
| QG-05 | Deterministic outputs | Re-evaluate same input snapshot in repeated pass | Equivalent check outcomes |
| QG-06 | Status and confidence validity | Check status enum and confidence range constraints | All records valid |

## Result Logging Template

Use this table to capture execution outputs:

| Test ID | Run ID | Status (Expected) | Status (Actual) | Conflicts (Expected) | Conflicts (Actual) | Confidence (Actual) | Pass/Fail | Notes |
|---|---|---|---|---|---|---:|---|---|
| P1-T01 |  |  |  |  |  |  |  |  |
| P1-T02 |  |  |  |  |  |  |  |  |
| P1-T03 |  |  |  |  |  |  |  |  |
| P1-T04 |  |  |  |  |  |  |  |  |
| P1-T05 |  |  |  |  |  |  |  |  |
| P1-T06 |  |  |  |  |  |  |  |  |
| P1-T07 |  |  |  |  |  |  |  |  |
| P1-T08 |  |  |  |  |  |  |  |  |
| P1-T09 |  |  |  |  |  |  |  |  |
| P1-T10 |  |  |  |  |  |  |  |  |

## Exit Criteria
Person 1 test completion is achieved when:
1. All quality gates pass.
2. No unresolved high-impact conflict is mislabeled as `confirmed`.
3. Determinism check passes for status, conflict, and confidence outputs.
4. All failed tests include corrective action notes and re-test evidence.
