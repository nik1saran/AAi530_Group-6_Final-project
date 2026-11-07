# Person 1 Decision Logic Specification

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Purpose
This document defines deterministic decision logic for Person 1 (Data Acquisition & Verification), including status assignment, conflict handling, freshness precedence, and confidence scoring.

## Inputs
Decision logic operates on normalized claims with the following minimum fields:
- `event_id`
- `event_type`
- `source_name`
- `source_tier`
- `source_url`
- `published_at_utc`
- `retrieved_at_utc`
- `location_name`
- `claim_text`
- impact fields (casualties/injuries/displaced/affected when available)

## Outputs
For each processed claim:
- `status` (`confirmed`, `preliminary`, `unverified`)
- `confidence_score` (`0.00`-`1.00`)
- `conflict_flags` (array)
- `conflict_details` (array)
- `evidence_notes` (string)
- supersession metadata (`is_superseded`, `supersedes_record_id`)

## Processing Pipeline

1. **Normalize**
   - Standardize timestamps to UTC.
   - Normalize location text and event-type labels.
   - Parse numeric impact fields to integers or `null`.

2. **Group**
   - Partition claims by `event_id` (or deterministic event key when `event_id` is first generated).

3. **Score Evidence**
   - Evaluate source quality, corroboration, freshness, and conflict state.

4. **Assign Status**
   - Apply deterministic status rules (Section: Status Logic).

5. **Attach Conflicts**
   - Detect and record contradictions with field-level evidence.

6. **Finalize Record**
   - Persist output with full provenance and audit notes.

## Status Logic

### Rule Set A - Confirmed
Assign `confirmed` only if all criteria hold:
1. Claim supported by Tier A source **or** by multiple independent high-credibility sources.
2. No unresolved high-impact conflict for core facts.
3. Claim is temporally current relative to the event stream.

Hard blocks for `confirmed`:
- `source_tier = tier_c` and no Tier A/B corroboration.
- Open conflict in casualties/location/timing/severity not resolved.
- Missing attribution metadata.

### Rule Set B - Preliminary
Assign `preliminary` when:
- Source is credible but evidence is incomplete or evolving, or
- Partial corroboration exists but material fields remain unstable.

### Rule Set C - Unverified
Assign `unverified` when any condition applies:
- Single-source non-authoritative claim.
- Contradictions are unresolved and materially impact interpretation.
- Provenance/timeliness does not meet minimum quality threshold.

## Conflict Detection Logic

For claims in the same event group, compare canonical fields:
- `casualties_reported`
- `injuries_reported`
- `displaced_reported`
- `location_name` / `location_geo`
- `published_at_utc` narrative sequencing
- emergency status/severity wording

Flag codes:
- `conflict_casualties`
- `conflict_injuries`
- `conflict_displaced`
- `conflict_location`
- `conflict_timing`
- `conflict_severity`
- `conflict_action_status`

Conflict handling policy:
- Preserve all conflicting values.
- Add field-specific entries in `conflict_details`.
- Reduce status ceiling to `preliminary` or `unverified` until resolved.

## Freshness and Supersession Logic

1. Prefer newer authoritative claims over older ones for active state.
2. Mark superseded records:
   - Older claim remains stored (`is_superseded=true`).
   - Newer record references old via `supersedes_record_id`.
3. Historical claims are retained for audit and timeline reconstruction.

## Confidence Scoring Model

`confidence_score` is deterministic and bounded to `[0.00, 1.00]`.

### Weighted Factors
- Source quality (`SQ`) = 0.35
- Corroboration strength (`CS`) = 0.25
- Freshness (`FR`) = 0.20
- Conflict penalty (`CP`) = 0.15
- Completeness (`CM`) = 0.05

### Formula
`confidence = (SQ + CS + FR + CM) - CP`

Clamp:
- `< 0.00` -> `0.00`
- `> 1.00` -> `1.00`

### Suggested Factor Mapping
- `SQ`: tier_a=0.35, tier_b=0.24, tier_c=0.10
- `CS`: none=0.00, one independent corroboration=0.15, strong multi-source=0.25
- `FR`: fresh=0.20, moderate lag=0.12, stale=0.05
- `CP`: no conflict=0.00, minor conflict=0.07, major unresolved conflict=0.15
- `CM`: complete critical fields=0.05, partial=0.02, sparse=0.00

## Status Threshold Guidance

Thresholds guide consistency but do not override hard rules:
- `>= 0.80`: eligible for `confirmed` if hard rules pass
- `0.45 - 0.79`: typically `preliminary`
- `< 0.45`: typically `unverified`

Hard rules always take precedence over thresholds.

## Evidence Notes Requirements
Each record must include concise rationale in `evidence_notes`, covering:
1. Why source quality level was assigned.
2. Whether corroboration exists.
3. Whether conflicts were detected.
4. Why current status was chosen.

## Determinism Requirements
- Same input snapshot must yield same status and confidence outputs.
- No random weighting, stochastic tie-breakers, or hidden heuristics.
- All policy constants must be version-controlled.

## Failure Handling
- If required attribution fields are missing, record is invalid and cannot be marked `confirmed`.
- If timestamp parsing fails, set status ceiling to `unverified` until corrected.
- If conflict evaluation cannot run, record processing is incomplete and must be flagged for manual review.

## Pseudocode

```text
for claim in normalized_claims:
  group = event_group(claim.event_id)
  conflicts = detect_conflicts(claim, group)
  factors = score_factors(claim, group, conflicts)
  confidence = clamp(factors.SQ + factors.CS + factors.FR + factors.CM - factors.CP, 0, 1)

  if hard_block_confirmed(claim, conflicts):
      status = preliminary_or_unverified_by_rules(claim, confidence, conflicts)
  else if confidence >= 0.80 and authoritative_or_strong_corroboration(claim, group):
      status = confirmed
  else if confidence >= 0.45:
      status = preliminary
  else:
      status = unverified

  emit_record(claim, status, confidence, conflicts, evidence_notes)
```

## Versioning
Any modification to:
- source-tier mappings,
- factor weights,
- threshold ranges,
- or conflict severity policy

must be logged with version number, date, and rationale.
