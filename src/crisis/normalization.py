from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import re
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
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_event_type(raw: str) -> str:
    normalized = (raw or "").strip().lower()
    return EVENT_TYPE_MAP.get(normalized, "other")


def safe_int(value: Any) -> int | None:
    if value in (None, "", "unknown"):
        return None
    return max(0, int(value))


def _normalize_location_text(text: str | None) -> str:
    if not text:
        return "unknown"
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return "_".join(cleaned.split(" ")[:3]) or "unknown"


def _canonical_event_id(record: dict[str, Any]) -> str:
    event_type = canonical_event_type(record.get("event_type", "other"))
    location_key = _normalize_location_text(record.get("location_name"))
    ts = record.get("published_at_utc") or record.get("retrieved_at_utc")
    if ts:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Daily bucket for declaration-style sources, hourly for fast-moving alerts.
        if "fema" in str(record.get("source_name", "")).lower():
            time_key = dt.strftime("%Y%m%d")
        else:
            time_key = dt.strftime("%Y%m%d%H")
    else:
        time_key = "unknown"
    return f"cev_{event_type}_{location_key}_{time_key}"


def idempotency_key(record: dict[str, Any]) -> str:
    basis = "|".join(
        [
            str(record.get("event_id", "")),
            str(record.get("source_event_id", "")),
            str(record.get("source_name", "")),
            str(record.get("source_url", "")),
            str(record.get("published_at_utc", "")),
            str(record.get("location_name", "")),
            str(record.get("claim_text", "")),
        ]
    )
    return sha256(basis.encode("utf-8")).hexdigest()


def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
    record = dict(raw)
    record["event_type"] = canonical_event_type(record.get("event_type", "other"))
    record["published_at_utc"] = to_utc_iso(record.get("published_at_utc"))
    record["retrieved_at_utc"] = to_utc_iso(record.get("retrieved_at_utc"))
    record["expires_at_utc"] = to_utc_iso(record.get("expires_at_utc"))
    record["last_updated_at_utc"] = to_utc_iso(record.get("last_updated_at_utc"))
    if record.get("source_event_id") is not None:
        record["source_event_id"] = str(record.get("source_event_id"))
    record["canonical_event_id"] = _canonical_event_id(record)
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
