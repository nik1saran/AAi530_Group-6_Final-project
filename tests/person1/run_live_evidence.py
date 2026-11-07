import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.person1.live_evidence import run_live_evidence_bundle
from tests.person1.validate_schema import validate


def _write_markdown(results_path: Path, payload: dict) -> None:
    lines = [
        f"# Person 1 Live Retrieval Results ({payload['run_id']})",
        "",
        f"- **Run ID:** `{payload['run_id']}`",
        f"- **Generated (UTC):** {payload['generated_at_utc']}",
        f"- **Input claims file:** `{payload['input_claims']}`",
        f"- **Validated output file:** `{payload['validated_output']}`",
        f"- **Schema validation:** {'PASS' if payload['schema_validation']['passed'] else 'FAIL'}",
        "",
        "## Source Fetch Log",
        "",
        "| Source | HTTP | Latency (ms) | Parsed records | Error | Raw file |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in payload["fetch_rows"]:
        lines.append(
            f"| {row['source_name']} | {row['http_status'] if row['http_status'] is not None else 'N/A'} | "
            f"{row['latency_ms']} | {row['record_count']} | {row['error'] or 'None'} | `{row['raw_file']}` |"
        )
    lines.append("")
    lines.append(f"## Output Record Count")
    lines.append(f"- `{payload['record_count']}` records in validated output")
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_evidence_doc(repo_root: Path, latest_payload: dict) -> None:
    log_path = repo_root / "logs" / "person1" / "live-fetch-log.jsonl"
    runs: dict[str, list[dict]] = {}
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            runs.setdefault(row["run_id"], []).append(row)

    run_ids = sorted(runs.keys(), reverse=True)[:5]
    doc = repo_root / "docs" / "person1" / "live-retrieval-evidence.md"
    lines = [
        "# Live Retrieval Evidence",
        "",
        "This document captures live API retrieval evidence for Person 1.",
        "",
        f"Latest run: `{latest_payload['run_id']}`",
        "",
        "## Recent Runs",
        "",
        "| Run ID | Source rows | Any errors |",
        "|---|---:|---|",
    ]
    for run_id in run_ids:
        rows = runs[run_id]
        has_error = any(r.get("error") for r in rows)
        lines.append(f"| {run_id} | {len(rows)} | {'Yes' if has_error else 'No'} |")

    lines += [
        "",
        "## Generated Artifacts per Run",
        "- `data/person1/live/raw/<run_id>/` (raw source payloads)",
        "- `data/person1/live/input-claims-<run_id>.json`",
        "- `data/person1/live/validated-output-<run_id>.json`",
        "- `tests/person1/live-test-results-<run_id>.md`",
        "- `tests/person1/live-test-results-<run_id>.json`",
        "- `logs/person1/live-fetch-log.jsonl`",
    ]
    doc.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    bundle = run_live_evidence_bundle(ROOT)
    run_id = bundle["run_id"]
    validated_output = bundle["validated_output"]

    schema_path = ROOT / "schemas" / "person1" / "verified-crisis-batch.schema.json"
    ok, message = validate(schema_path, validated_output)

    results = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_claims": str(bundle["input_claims"].relative_to(ROOT)).replace("\\", "/"),
        "validated_output": str(validated_output.relative_to(ROOT)).replace("\\", "/"),
        "record_count": bundle["record_count"],
        "schema_validation": {"passed": ok, "message": message},
        "fetch_rows": bundle["fetch_rows"],
    }

    out_json = ROOT / "tests" / "person1" / f"live-test-results-{run_id}.json"
    out_md = ROOT / "tests" / "person1" / f"live-test-results-{run_id}.md"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    _write_markdown(out_md, results)
    _update_evidence_doc(ROOT, results)

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")
    print(f"Schema validation: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

