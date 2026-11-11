from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .audit import append_manifest, build_manifest
from .normalization import normalize_record
from .verification import verify_records


def run_fixture_pipeline(input_path: Path, output_path: Path, manifest_path: Path, log_manifest: bool = True) -> dict:
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%SZ')}"
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    raw_records = payload.get("records", [])

    dedup = {}
    normalized = []
    dead_letter_path = manifest_path.parent / "dead-letter.jsonl"
    for raw in raw_records:
        record = normalize_record(raw)
        required = ["record_id", "event_id", "source_name", "source_url", "source_tier", "retrieved_at_utc", "claim_text", "location_name"]
        missing = [k for k in required if record.get(k) in (None, "")]
        if missing:
            append_manifest(
                dead_letter_path,
                {
                    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "reason": "missing_required_fields",
                    "missing_fields": missing,
                    "record": record,
                },
            )
            continue
        if record["ingestion_key"] in dedup:
            continue
        dedup[record["ingestion_key"]] = True
        normalized.append(record)

    verified = verify_records(normalized)
    for r in verified:
        r["ingestion_run_id"] = run_id

    active_records = [r for r in verified if r.get("is_active", True)]
    batch = {
        "ingestion_run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "records": verified,
        "active_records": active_records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(batch, indent=2), encoding="utf-8")

    if log_manifest:
        manifest = build_manifest(input_path, output_path, run_id)
        append_manifest(manifest_path, manifest)
    return batch
