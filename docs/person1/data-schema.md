# Person 1 Data Schema Specification

## Project
**Public Catastrophic Crisis Briefing Assistant**

## Purpose
This schema defines the canonical output format for Person 1 (Data Acquisition & Verification). It standardizes ingested and verified crisis records for downstream consumption by AI summarization, crisis analysis, and interface components.

## Design Principles
- Deterministic structure across all records
- Full source attribution and temporal traceability
- Explicit uncertainty and conflict representation
- No inferred critical values without evidence

## Record Entity: `verified_crisis_record`

Each row/object represents one normalized claim snapshot tied to a specific event context.

## Field Definitions

| Field | Type | Required | Allowed Values / Format | Description |
|---|---|---:|---|---|
| `record_id` | string | Yes | UUID or deterministic hash | Unique record identifier |
| `event_id` | string | Yes | Stable event key | Groups records tied to same incident |
| `event_type` | string | Yes | Controlled vocabulary | Hazard category (earthquake, flood, wildfire, cyclone, epidemic, etc.) |
| `source_name` | string | Yes | Free text | Human-readable source identity |
| `source_url` | string | Yes | Valid URL | Link to originating source |
| `source_tier` | string | Yes | `tier_a`, `tier_b`, `tier_c` | Source hierarchy class |
| `published_at_utc` | string | Yes* | ISO 8601 UTC | Source publication/update timestamp; use `null` only if unavailable |
| `retrieved_at_utc` | string | Yes | ISO 8601 UTC | Time system ingested this record |
| `location_name` | string | Yes | Free text | Canonical location label |
| `location_geo` | object | No | `{ "lat": number, "lon": number }` | Optional normalized coordinates |
| `country_code` | string | No | ISO-3166-1 alpha-2 | Country code for analytics/filtering |
| `casualties_reported` | integer | No | `>= 0` or `null` | Reported fatalities count |
| `injuries_reported` | integer | No | `>= 0` or `null` | Reported injuries count |
| `missing_reported` | integer | No | `>= 0` or `null` | Reported missing persons |
| `displaced_reported` | integer | No | `>= 0` or `null` | Reported displaced population |
| `affected_population_reported` | integer | No | `>= 0` or `null` | Estimated affected population |
| `infrastructure_impact` | string | No | Free text / controlled tags | Key impact notes |
| `emergency_actions` | array[string] | No | Action strings | Evacuation, shelter activation, alerts, closures, etc. |
| `claim_text` | string | Yes | Free text | Normalized factual claim snippet |
| `status` | string | Yes | `confirmed`, `preliminary`, `unverified` | Verification status |
| `confidence_score` | number | Yes | `0.00` to `1.00` | Deterministic confidence output |
| `conflict_flags` | array[string] | Yes | Flag codes | Contradictions detected for this claim |
| `conflict_details` | array[object] | No | Structured conflict notes | Field-level discrepancy evidence |
| `supersedes_record_id` | string | No | Existing `record_id` | Links new update replacing stale claim |
| `is_superseded` | boolean | Yes | `true` / `false` | Indicates whether this record is outdated |
| `evidence_notes` | string | Yes | Free text | Why this status and score were assigned |
| `ingestion_run_id` | string | Yes | UUID/hash | Batch/run traceability key |

## Controlled Vocabularies

### `status`
- `confirmed`
- `preliminary`
- `unverified`

### `source_tier`
- `tier_a` — authoritative
- `tier_b` — institutional
- `tier_c` — signal-only

### `event_type` (minimum set)
- `earthquake`
- `flood`
- `wildfire`
- `storm`
- `hurricane`
- `landslide`
- `epidemic`
- `industrial_accident`
- `conflict_related_humanitarian`
- `other`

### `conflict_flags` (recommended codes)
- `conflict_casualties`
- `conflict_injuries`
- `conflict_displaced`
- `conflict_location`
- `conflict_timing`
- `conflict_severity`
- `conflict_action_status`

## Validation Rules

1. `source_name`, `source_url`, `retrieved_at_utc`, `status`, and `evidence_notes` are mandatory.
2. `status=confirmed` is invalid when:
   - `source_tier=tier_c`, or
   - `conflict_flags` contains unresolved high-impact conflicts.
3. Numeric impact fields must be non-negative integers or `null` (no negative, no strings).
4. Timestamps must be ISO 8601 UTC.
5. Unknown critical values must remain explicit (`null`), never guessed.
6. `is_superseded=true` requires either `supersedes_record_id` linkage in newer record lineage or explicit archival reason.

## JSON Shape (Reference)

```json
{
  "record_id": "b2df2c9f-85f2-4d41-94ef-f3d963bfc86d",
  "event_id": "event_2026_11_earthquake_001",
  "event_type": "earthquake",
  "source_name": "USGS",
  "source_url": "https://example.org/event/123",
  "source_tier": "tier_a",
  "published_at_utc": "2026-11-06T21:58:00Z",
  "retrieved_at_utc": "2026-11-06T22:00:15Z",
  "location_name": "Offshore Northern California",
  "location_geo": { "lat": 40.12, "lon": -124.35 },
  "country_code": "US",
  "casualties_reported": null,
  "injuries_reported": null,
  "missing_reported": null,
  "displaced_reported": null,
  "affected_population_reported": null,
  "infrastructure_impact": "No confirmed structural damage at retrieval time.",
  "emergency_actions": ["tsunami_assessment_in_progress"],
  "claim_text": "Magnitude 6.8 earthquake detected offshore Northern California.",
  "status": "preliminary",
  "confidence_score": 0.82,
  "conflict_flags": [],
  "conflict_details": [],
  "supersedes_record_id": null,
  "is_superseded": false,
  "evidence_notes": "Tier A source with fresh timestamp; impact fields pending corroboration.",
  "ingestion_run_id": "run_20261106_2200z"
}
```

## Output Containers

### Batch Envelope: `verified_crisis_batch`

```json
{
  "ingestion_run_id": "run_20261106_2200z",
  "generated_at_utc": "2026-11-06T22:00:30Z",
  "records": []
}
```

Required batch metadata:
- `ingestion_run_id`
- `generated_at_utc`
- `records` (array of `verified_crisis_record`)

## Compatibility Contract
Downstream components can assume:
- Stable required fields remain present in every record
- Status semantics are fixed (`confirmed`, `preliminary`, `unverified`)
- Conflicts are explicit and not silently resolved
- Evidence and provenance are available per claim

## Machine-Enforced Schema Artifact
Canonical schema file:
- `schemas/person1/verified-crisis-batch.schema.json`

Validation entrypoint:
- `python .\tests\person1\validate_schema.py`
