from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


EVENT_TYPE_MAP = {
    "quake": "earthquake",
    "earthquake": "earthquake",
    "flood": "flood",
    "wildfire": "wildfire",
    "storm": "storm",
    "hurricane": "hurricane",
    "epidemic": "epidemic",
}


def to_utc_iso(ts: str | None) -> str | None:
    if not ts:
        return None
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_event_type(raw: str) -> str:
    normalized = (raw or "").strip().lower()
    return EVENT_TYPE_MAP.get(normalized, "other")


def safe_int(value: Any) -> int | None:
    if value in (None, "", "unknown"):
        return None
    return max(0, int(value))


def idempotency_key(record: dict[str, Any]) -> str:
    basis = "|".join(
        [
            str(record.get("event_id", "")),
            str(record.get("source_name", "")),
            str(record.get("source_url", "")),
            str(record.get("published_at_utc", "")),
            str(record.get("claim_text", "")),
        ]
    )
    return sha256(basis.encode("utf-8")).hexdigest()


def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
    record = dict(raw)
    record["event_type"] = canonical_event_type(record.get("event_type", "other"))
    record["published_at_utc"] = to_utc_iso(record.get("published_at_utc"))
    record["retrieved_at_utc"] = to_utc_iso(record.get("retrieved_at_utc"))
    for key in [
        "casualties_reported",
        "injuries_reported",
        "missing_reported",
        "displaced_reported",
        "affected_population_reported",
    ]:
        record[key] = safe_int(record.get(key))
    record["ingestion_key"] = idempotency_key(record)
    return record

