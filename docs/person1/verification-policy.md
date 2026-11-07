# Data Acquisition & Verification Policy

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Purpose
This policy defines how incoming crisis data is sourced, verified, classified, and preserved for downstream analysis and briefing generation. The objective is to ensure that all ingested information is traceable, quality-scored, and transparently labeled by confidence and verification state.

## Scope
This policy applies to Person 1 deliverables only:
- Source selection and ingestion
- Source attribution and timestamping
- Credibility assessment
- Conflict detection
- Verification classification (`confirmed`, `preliminary`, `unverified`)

Out of scope:
- LLM summarization
- Trend interpretation and executive briefing composition
- UI rendering and release workflows

## Source Hierarchy

### Tier A — Authoritative Sources
Official emergency agencies, government departments, and designated intergovernmental organizations.

Examples:
- USGS
- NOAA / National Weather Service
- FEMA
- CDC
- WHO

Usage rule:
- Tier A can directly support `confirmed` status when event details are coherent and current.

### Tier B — Institutional Sources
Established organizations and high-reliability operational partners with structured reporting.

Examples:
- GDACS
- ReliefWeb
- National or state emergency operation centers

Usage rule:
- Tier B supports `preliminary` status by default and can contribute to `confirmed` when corroborated by Tier A or multiple independent high-quality sources.

### Tier C — Signal Sources
Unofficial, crowdsourced, social, or unstructured early-warning reports.

Usage rule:
- Tier C cannot independently produce `confirmed` status.
- Tier C may be retained as an `unverified` lead pending corroboration.

## Required Record-Level Metadata
Every ingested claim must include:
- `source_name`
- `source_url`
- `retrieved_at_utc`
- `published_at_utc` (or equivalent source timestamp; `null` only when unavailable)
- `event_type`
- `location_name`
- `claim_text`
- `status`
- `confidence_score`
- `conflict_flags`
- `evidence_notes`

Records without attribution and retrieval timestamp are invalid.

## Verification Classification Rules

### Confirmed
Assign `confirmed` when one of the following is true:
1. Tier A source provides clear, current, and internally consistent evidence for the claim.
2. Two or more independent high-credibility sources align on core facts with no unresolved high-impact conflicts.

### Preliminary
Assign `preliminary` when:
- Information is credible but incomplete, evolving, or partially corroborated.
- Evidence exists but critical attributes (magnitude, casualty count, affected area) remain unstable.

### Unverified
Assign `unverified` when:
- Claim is single-source and non-authoritative.
- Sources are contradictory without clear resolution.
- Timeliness, provenance, or claim quality is insufficient for operational confidence.

## Conflict Detection Rules
Conflicts must be flagged explicitly when claims for the same incident disagree on:
- Fatalities, injuries, missing, displaced, or affected population totals
- Event location or impacted geography
- Event timing (onset/update chronology)
- Declared severity or emergency level

When conflicts exist:
- Preserve all conflicting claims with linked evidence.
- Keep status at `preliminary` or `unverified` until resolved.
- Never auto-upgrade to `confirmed` while material conflict remains open.

## Freshness and Timeliness Rules
- Prefer the most recent authoritative update when multiple reports exist.
- Mark stale records when newer authoritative records supersede them.
- Retain historical claims for audit, but expose supersession status in metadata.

## Confidence Scoring Policy
`confidence_score` must be deterministic and policy-driven. Recommended inputs:
- Source tier quality
- Corroboration count and independence
- Timestamp freshness
- Presence/absence of unresolved conflicts
- Completeness of key fields

Confidence scores must be accompanied by `evidence_notes` describing the primary reason for the assigned value.

## Source-of-Truth Principle
No single feed is treated as universal truth for all fields. Source-of-truth is field-specific and evidence-weighted:
- Authoritative agencies have precedence for event facts and warnings.
- Institutional and humanitarian sources provide supplemental context.
- Contradictions remain visible and are not silently normalized.

## Data Integrity Requirements
- No silent field imputation for critical values (casualties, location, event timing).
- Unknown values remain explicit (`null`/`unknown`) rather than guessed.
- Every status decision must be reproducible from stored evidence.

## Quality Gates
The pipeline is acceptable only when all conditions are met:
1. 100% of records include attribution and retrieval timestamp.
2. 0 records are marked `confirmed` without policy-compliant evidence.
3. All material conflicts are explicitly flagged.
4. Re-running on the same input snapshot yields equivalent status outcomes.
5. Audit fields are complete for downstream traceability.

## Governance
This policy is versioned and updated only through explicit revision entries. Any changes to status logic, source hierarchy, or confidence scoring must include rationale and effective date.
