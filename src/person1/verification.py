from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from .config import (
    ALLOWED_SOURCE_TIERS,
    COMPLETENESS_SCORE,
    CONFLICT_PENALTY,
    CORROBORATION_SCORE,
    FRESHNESS_SCORE,
    SOURCE_QUALITY_SCORE,
    THRESHOLDS,
)


def _age_hours(ts: str | None) -> float:
    if not ts:
        return 10_000
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - parsed
    return max(0.0, delta.total_seconds() / 3600)


def _freshness_bucket(ts: str | None) -> str:
    age = _age_hours(ts)
    if age <= 3:
        return "fresh"
    if age <= THRESHOLDS.max_staleness_hours:
        return "moderate"
    return "stale"


def _completeness(record: dict[str, Any]) -> str:
    critical = ["source_name", "source_url", "retrieved_at_utc", "claim_text", "location_name"]
    present = sum(1 for k in critical if record.get(k) not in (None, ""))
    if present == len(critical):
        return "complete"
    if present >= 3:
        return "partial"
    return "sparse"


def _detect_conflicts(records: list[dict[str, Any]]) -> dict[str, dict[str, list[Any]]]:
    conflicts: dict[str, dict[str, list[Any]]] = defaultdict(lambda: {"flags": [], "details": []})
    numeric_fields = ["casualties_reported", "injuries_reported", "displaced_reported"]

    for field in numeric_fields:
        values = {r["record_id"]: r.get(field) for r in records if r.get(field) is not None}
        if len(set(values.values())) > 1:
            for rid in values:
                conflicts[rid]["flags"].append(f"conflict_{field.replace('_reported', '')}")
                conflicts[rid]["details"].append(
                    {
                        "field": field,
                        "values_seen": sorted(list(set(values.values()))),
                        "note": "Numeric discrepancy detected across sources for same event.",
                    }
                )

    locations = {r["record_id"]: r.get("location_name") for r in records if r.get("location_name")}
    if len(set(locations.values())) > 1:
        for rid in locations:
            conflicts[rid]["flags"].append("conflict_location")
            conflicts[rid]["details"].append(
                {
                    "field": "location_name",
                    "values_seen": sorted(list(set(locations.values()))),
                    "note": "Location mismatch detected across sources for same event.",
                }
            )

    return conflicts


def _score(record: dict[str, Any], corroboration_count: int, has_major_conflict: bool) -> float:
    sq = SOURCE_QUALITY_SCORE.get(record.get("source_tier", ""), 0.0)
    cs = CORROBORATION_SCORE.get(min(corroboration_count, 2), CORROBORATION_SCORE[2])
    fr = FRESHNESS_SCORE[_freshness_bucket(record.get("published_at_utc"))]
    cm = COMPLETENESS_SCORE[_completeness(record)]
    cp = CONFLICT_PENALTY["major" if has_major_conflict else "none"]
    return max(0.0, min(1.0, sq + cs + fr + cm - cp))


def _classify(record: dict[str, Any], confidence: float, has_major_conflict: bool) -> str:
    tier = record.get("source_tier")
    missing_attribution = any(
        record.get(k) in (None, "")
        for k in ["source_name", "source_url", "retrieved_at_utc", "claim_text"]
    )
    if missing_attribution:
        return "unverified"
    if tier not in ALLOWED_SOURCE_TIERS:
        return "unverified"
    if has_major_conflict:
        return "preliminary" if confidence >= THRESHOLDS.preliminary_min else "unverified"
    if tier == "tier_c":
        return "unverified"
    if confidence >= THRESHOLDS.confirmed_min:
        return "confirmed"
    if confidence >= THRESHOLDS.preliminary_min:
        return "preliminary"
    return "unverified"


def verify_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        by_event[r["event_id"]].append(r)

    verified: list[dict[str, Any]] = []
    for _, group in by_event.items():
        conflicts = _detect_conflicts(group)
        source_set = {(r.get("source_name"), r.get("source_url")) for r in group}
        corroboration_count = max(0, len(source_set) - 1)

        # Supersession by event and source recency
        newest = sorted(
            group,
            key=lambda r: r.get("published_at_utc") or "",
            reverse=True,
        )
        newest_id = newest[0]["record_id"] if newest else None

        for r in group:
            conflict_info = conflicts.get(r["record_id"], {"flags": [], "details": []})
            conflict_flags = conflict_info["flags"]
            has_major_conflict = bool(conflict_flags)
            confidence = round(_score(r, corroboration_count, has_major_conflict), 2)
            status = _classify(r, confidence, has_major_conflict)

            out = dict(r)
            out["confidence_score"] = confidence
            out["status"] = status
            out["conflict_flags"] = conflict_flags
            out["conflict_details"] = conflict_info["details"]
            out["is_superseded"] = r["record_id"] != newest_id
            out["supersedes_record_id"] = newest_id if r["record_id"] != newest_id else None
            out["evidence_notes"] = (
                f"tier={r.get('source_tier')} corroboration={corroboration_count} "
                f"freshness={_freshness_bucket(r.get('published_at_utc'))} conflicts={len(conflict_flags)}"
            )
            verified.append(out)

    return verified
