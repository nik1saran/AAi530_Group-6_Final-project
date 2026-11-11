import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.crisis.pipeline import run_fixture_pipeline

FIXTURE_FILE = ROOT / "tests" / "fixtures" / "input-claims.json"
OUT_JSON = ROOT / "data" / "sample-validated-output.json"
OUT_RESULTS_JSON = ROOT / "tests" / "test-results.json"
OUT_RESULTS_MD = ROOT / "tests" / "test-results.md"
MANIFEST_JSONL = ROOT / "logs" / "run-manifest.jsonl"

REQUIRED_FIELDS = [
    "source_name",
    "source_url",
    "retrieved_at_utc",
    "status",
    "evidence_notes",
]
ALLOWED_STATUS = {"confirmed", "preliminary", "unverified"}


def is_iso_utc(ts: str | None) -> bool:
    if not ts:
        return False
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _run_checks(batch: dict[str, Any], deterministic: bool) -> list[dict[str, Any]]:
    records = batch.get("records", [])
    active_records = batch.get("active_records", [])
    checks: list[dict[str, Any]] = []

    qg01 = []
    for r in records:
        rid = r.get("record_id", "<missing_record_id>")
        for f in REQUIRED_FIELDS:
            if r.get(f) in (None, ""):
                qg01.append(f"{rid}: missing {f}")
        if not is_iso_utc(r.get("retrieved_at_utc")):
            qg01.append(f"{rid}: invalid retrieved_at_utc")
    checks.append({"id": "QG-01", "name": "Attribution coverage", "passed": len(qg01) == 0, "details": qg01})

    qg02 = []
    for r in records:
        if r.get("status") == "confirmed":
            rid = r.get("record_id", "<missing_record_id>")
            if r.get("source_tier") == "tier_c":
                qg02.append(f"{rid}: tier_c cannot be confirmed")
            if r.get("conflict_flags"):
                qg02.append(f"{rid}: confirmed with unresolved conflicts")
    checks.append({"id": "QG-02", "name": "No unsupported confirmations", "passed": len(qg02) == 0, "details": qg02})

    qg03 = []
    has_conflicts = any((r.get("conflict_flags") or []) for r in records)
    if not has_conflicts:
        qg03.append("No conflicts found in dataset; expected at least one scenario.")
    for r in records:
        rid = r.get("record_id", "<missing_record_id>")
        flags = r.get("conflict_flags") or []
        details = r.get("conflict_details") or []
        if flags and not details:
            qg03.append(f"{rid}: conflict_flags present but conflict_details empty")
        if flags and not isinstance(details, list):
            qg03.append(f"{rid}: conflict_details must be array")
    checks.append({"id": "QG-03", "name": "Conflict transparency", "passed": len(qg03) == 0, "details": qg03})

    qg04 = []
    ids = {r.get("record_id") for r in records}
    for r in records:
        sup = r.get("supersedes_record_id")
        if sup and sup not in ids:
            qg04.append(f"{r.get('record_id')}: supersedes_record_id not found ({sup})")
    checks.append({"id": "QG-04", "name": "Freshness precedence", "passed": len(qg04) == 0, "details": qg04})

    qg05 = []
    if not deterministic:
        qg05.append("Canonical record outputs differ between repeated pipeline runs.")
    checks.append({"id": "QG-05", "name": "Deterministic outputs", "passed": len(qg05) == 0, "details": qg05})

    qg06 = []
    for r in records:
        rid = r.get("record_id", "<missing_record_id>")
        status = r.get("status")
        conf = r.get("confidence_score")
        if status not in ALLOWED_STATUS:
            qg06.append(f"{rid}: invalid status ({status})")
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            qg06.append(f"{rid}: confidence out of range ({conf})")
        pub = r.get("published_at_utc")
        ret = r.get("retrieved_at_utc")
        if pub and ret and pub > ret:
            qg06.append(f"{rid}: published_at_utc > retrieved_at_utc")
    checks.append({"id": "QG-06", "name": "Status and confidence validity", "passed": len(qg06) == 0, "details": qg06})

    qg07 = []
    # Ensure FEMA county-level rows are retained (no over-aggressive dedupe).
    fema_rows = [r for r in records if r.get("source_name") == "FEMA Open Data" and str(r.get("source_event_id", "")).startswith("4955:")]
    county_names = {r.get("source_metadata", {}).get("fema_county") for r in fema_rows}
    if len(county_names) < 2:
        qg07.append("FEMA county-level records were collapsed; expected at least two county variants for disaster 4955.")
    # Active records should not include expired or superseded entries.
    for r in active_records:
        if r.get("is_superseded"):
            qg07.append(f"{r.get('record_id')}: superseded record present in active_records.")
        if r.get("is_active") is False:
            qg07.append(f"{r.get('record_id')}: inactive record present in active_records.")
    checks.append({"id": "QG-07", "name": "Lifecycle filtering and FEMA county retention", "passed": len(qg07) == 0, "details": qg07})

    return checks


def main() -> int:
    batch = run_fixture_pipeline(FIXTURE_FILE, OUT_JSON, MANIFEST_JSONL)
    det_output = ROOT / "logs" / "_determinism-output.json"
    det_batch = run_fixture_pipeline(FIXTURE_FILE, det_output, MANIFEST_JSONL, log_manifest=False)

    def canonicalize(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        canon = []
        for item in items:
            copy = dict(item)
            copy.pop("ingestion_run_id", None)
            canon.append(copy)
        return sorted(canon, key=lambda x: x.get("record_id", ""))

    deterministic = canonicalize(batch.get("records", [])) == canonicalize(det_batch.get("records", []))
    if det_output.exists():
        det_output.unlink()

    checks = _run_checks(batch, deterministic)

    records = batch.get("records", [])
    active_records = batch.get("active_records", [])
    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    result = {
        "input_file": str(FIXTURE_FILE.relative_to(ROOT)),
        "output_file": str(OUT_JSON.relative_to(ROOT)),
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "record_count": len(records),
        "active_record_count": len(active_records),
        "summary": {
            "total_checks": len(checks),
            "passed_checks": passed,
            "failed_checks": failed,
            "overall_pass": failed == 0,
        },
        "checks": checks,
    }
    OUT_RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Validation Results",
        "",
        f"- **Input:** `{result['input_file']}`",
        f"- **Output:** `{result['output_file']}`",
        f"- **Generated (UTC):** {result['generated_at_utc']}",
        f"- **Records evaluated:** {result['record_count']}",
        f"- **Active records:** {result['active_record_count']}",
        f"- **Overall:** {'PASS' if result['summary']['overall_pass'] else 'FAIL'}",
        "",
        "| Check ID | Check | Status | Notes |",
        "|---|---|---|---|",
    ]
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        notes = "None" if not c["details"] else "; ".join(c["details"])
        lines.append(f"| {c['id']} | {c['name']} | {status} | {notes} |")
    OUT_RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_RESULTS_JSON}")
    print(f"Wrote: {OUT_RESULTS_MD}")
    print(f"Overall: {'PASS' if result['summary']['overall_pass'] else 'FAIL'}")
    return 0 if result["summary"]["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
