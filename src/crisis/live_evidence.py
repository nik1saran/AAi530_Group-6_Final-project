from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pipeline import run_fixture_pipeline


@dataclass(frozen=True)
class LiveSource:
    source_id: str
    source_name: str
    source_url: str
    source_tier: str
    parser_key: str


LIVE_SOURCES = [
    LiveSource(
        source_id="usgs_eq",
        source_name="USGS Earthquake Hazards Program",
        source_url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        source_tier="tier_a",
        parser_key="usgs",
    ),
    LiveSource(
        source_id="noaa_alerts",
        source_name="NOAA National Weather Service Alerts",
        source_url="https://api.weather.gov/alerts/active",
        source_tier="tier_a",
        parser_key="noaa",
    ),
    LiveSource(
        source_id="fema_disasters",
        source_name="FEMA Open Data",
        source_url="https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$top=25&$orderby=declarationDate%20desc",
        source_tier="tier_a",
        parser_key="fema",
    ),
]


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


def _fetch_json(url: str, timeout: int = 20) -> tuple[int | None, int, Any, str | None]:
    headers = {"User-Agent": "crisis-live-evidence/1.0", "Accept": "application/json, application/geo+json"}
    start = time.perf_counter()
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            data = json.loads(body)
            latency_ms = int((time.perf_counter() - start) * 1000)
            return status, latency_ms, data, None
    except urllib.error.HTTPError as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return exc.code, latency_ms, None, f"HTTPError: {exc}"
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return None, latency_ms, None, str(exc)


def _record_base(
    *,
    run_id: str,
    source: LiveSource,
    retrieved_at_utc: str,
    record_id: str,
    event_id: str,
    event_type: str,
    published_at_utc: str | None,
    location_name: str,
    claim_text: str,
    casualties_reported: int | None = None,
    injuries_reported: int | None = None,
    source_event_id: str | None = None,
    expires_at_utc: str | None = None,
    last_updated_at_utc: str | None = None,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "event_id": event_id,
        "event_type": event_type,
        "source_name": source.source_name,
        "source_url": source.source_url,
        "source_tier": source.source_tier,
        "published_at_utc": published_at_utc,
        "retrieved_at_utc": retrieved_at_utc,
        "location_name": location_name,
        "claim_text": claim_text,
        "casualties_reported": casualties_reported,
        "injuries_reported": injuries_reported,
        "missing_reported": None,
        "displaced_reported": None,
        "affected_population_reported": None,
        "source_event_id": source_event_id,
        "expires_at_utc": expires_at_utc,
        "last_updated_at_utc": last_updated_at_utc,
        "source_metadata": source_metadata or {},
    }


def _parse_usgs(run_id: str, source: LiveSource, retrieved_at_utc: str, payload: Any) -> list[dict[str, Any]]:
    features = payload.get("features", []) if isinstance(payload, dict) else []
    out = []
    for i, feature in enumerate(features[:8], start=1):
        props = feature.get("properties", {}) if isinstance(feature, dict) else {}
        feature_id = feature.get("id") if isinstance(feature, dict) else None
        event_time_ms = props.get("time")
        published = None
        if isinstance(event_time_ms, (int, float)):
            published = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        updated_ms = props.get("updated")
        updated = None
        if isinstance(updated_ms, (int, float)):
            updated = datetime.fromtimestamp(updated_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mag = props.get("mag")
        place = props.get("place") or "Unknown location"
        event_id = f"live_usgs_{props.get('ids') or feature_id or i}"
        claim = f"USGS reports earthquake magnitude {mag} near {place}."
        out.append(
            _record_base(
                run_id=run_id,
                source=source,
                retrieved_at_utc=retrieved_at_utc,
                record_id=f"{run_id}_usgs_{i}",
                event_id=event_id,
                event_type="earthquake",
                published_at_utc=published,
                location_name=str(place),
                claim_text=claim,
                source_event_id=str(feature_id or props.get("ids") or i),
                last_updated_at_utc=updated,
                source_metadata={
                    "usgs_alert": props.get("alert"),
                    "usgs_tsunami": props.get("tsunami"),
                    "usgs_felt": props.get("felt"),
                    "usgs_sig": props.get("sig"),
                    "usgs_mag": props.get("mag"),
                },
            )
        )
    return out


def _parse_noaa(run_id: str, source: LiveSource, retrieved_at_utc: str, payload: Any) -> list[dict[str, Any]]:
    features = payload.get("features", []) if isinstance(payload, dict) else []
    out = []
    for i, feature in enumerate(features[:8], start=1):
        props = feature.get("properties", {}) if isinstance(feature, dict) else {}
        feature_id = feature.get("id") if isinstance(feature, dict) else None
        event = props.get("event") or "Weather alert"
        area = props.get("areaDesc") or "Unknown area"
        sent = props.get("sent") or props.get("effective")
        updated = props.get("updated") or props.get("onset") or sent
        expires = props.get("expires")
        event_id = f"live_noaa_{feature_id or i}"
        claim = f"NOAA alert '{event}' for {area}."
        out.append(
            _record_base(
                run_id=run_id,
                source=source,
                retrieved_at_utc=retrieved_at_utc,
                record_id=f"{run_id}_noaa_{i}",
                event_id=event_id,
                event_type="storm",
                published_at_utc=sent,
                location_name=str(area),
                claim_text=claim,
                source_event_id=str(feature_id or i),
                expires_at_utc=expires,
                last_updated_at_utc=updated,
                source_metadata={
                    "noaa_event": event,
                    "noaa_description": props.get("description"),
                    "noaa_severity": props.get("severity"),
                    "noaa_urgency": props.get("urgency"),
                    "noaa_instruction": props.get("instruction"),
                    "noaa_sender": props.get("senderName"),
                },
            )
        )
    return out


def _parse_fema(run_id: str, source: LiveSource, retrieved_at_utc: str, payload: Any) -> list[dict[str, Any]]:
    entries = payload.get("DisasterDeclarationsSummaries", []) if isinstance(payload, dict) else []
    out = []
    for i, item in enumerate(entries[:8], start=1):
        state = item.get("state") or "Unknown state"
        incident_type = item.get("incidentType") or "Disaster"
        declaration_title = item.get("declarationTitle") or incident_type
        county = item.get("designatedArea") or item.get("placeCode") or "Unknown county/area"
        date = item.get("declarationDate")
        disaster_number = item.get("disasterNumber") or i
        event_id = f"live_fema_{disaster_number}"
        source_event_id = f"{disaster_number}:{county}"
        claim = f"FEMA declaration {disaster_number} ({declaration_title}) for {county}, {state}."
        out.append(
            _record_base(
                run_id=run_id,
                source=source,
                retrieved_at_utc=retrieved_at_utc,
                record_id=f"{run_id}_fema_{i}",
                event_id=event_id,
                event_type="other",
                published_at_utc=date,
                location_name=f"{county}, {state}",
                claim_text=claim,
                source_event_id=str(source_event_id),
                source_metadata={
                    "fema_disaster_number": disaster_number,
                    "fema_incident_type": incident_type,
                    "fema_declaration_title": declaration_title,
                    "fema_county": county,
                    "fema_state": state,
                },
            )
        )
    return out


PARSERS = {
    "usgs": _parse_usgs,
    "noaa": _parse_noaa,
    "fema": _parse_fema,
}


def run_live_evidence_bundle(repo_root: Path) -> dict[str, Any]:
    run_id = f"live_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%SZ')}"
    raw_dir = repo_root / "data" / "live" / "raw" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = repo_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    fetch_log_file = logs_dir / "live-fetch-log.jsonl"

    records: list[dict[str, Any]] = []
    fetch_rows: list[dict[str, Any]] = []

    for source in LIVE_SOURCES:
        retrieved = _now_utc()
        status, latency_ms, payload, error = _fetch_json(source.source_url)
        safe_name = _safe_filename(source.source_id)
        raw_file = raw_dir / f"{safe_name}.json"

        if payload is not None:
            raw_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            parser = PARSERS[source.parser_key]
            parsed = parser(run_id, source, retrieved, payload)
            records.extend(parsed)
            record_count = len(parsed)
        else:
            raw_file.write_text(json.dumps({"error": error, "source_url": source.source_url}, indent=2), encoding="utf-8")
            record_count = 0

        row = {
            "run_id": run_id,
            "source_id": source.source_id,
            "source_name": source.source_name,
            "source_url": source.source_url,
            "retrieved_at_utc": retrieved,
            "http_status": status,
            "latency_ms": latency_ms,
            "record_count": record_count,
            "error": error,
            "raw_file": str(raw_file.relative_to(repo_root)).replace("\\", "/"),
        }
        fetch_rows.append(row)
        with fetch_log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

    input_claims = repo_root / "data" / "live" / f"input-claims-{run_id}.json"
    input_claims.parent.mkdir(parents=True, exist_ok=True)
    input_claims.write_text(json.dumps({"records": records}, indent=2), encoding="utf-8")

    validated_output = repo_root / "data" / "live" / f"validated-output-{run_id}.json"
    manifest_path = repo_root / "logs" / "run-manifest.jsonl"
    batch = run_fixture_pipeline(input_claims, validated_output, manifest_path, log_manifest=True)

    return {
        "run_id": run_id,
        "input_claims": input_claims,
        "validated_output": validated_output,
        "fetch_rows": fetch_rows,
        "record_count": len(batch.get("records", [])),
    }
