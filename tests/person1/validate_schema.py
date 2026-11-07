import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "person1" / "verified-crisis-batch.schema.json"
DATA_PATH = ROOT / "data" / "person1" / "sample-validated-output.json"


def validate(schema_path: Path, data_path: Path) -> tuple[bool, str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))

    required_batch = schema["required"]
    missing_batch = [k for k in required_batch if k not in data]
    if missing_batch:
        return False, f"Missing batch fields: {missing_batch}"

    record_schema = schema["properties"]["records"]["items"]
    required_record = record_schema["required"]
    enum_status = set(record_schema["properties"]["status"]["enum"])
    enum_tier = set(record_schema["properties"]["source_tier"]["enum"])

    for idx, rec in enumerate(data.get("records", []), start=1):
        missing = [k for k in required_record if k not in rec]
        if missing:
            return False, f"record[{idx}] missing required fields: {missing}"
        if rec.get("status") not in enum_status:
            return False, f"record[{idx}] invalid status: {rec.get('status')}"
        if rec.get("source_tier") not in enum_tier:
            return False, f"record[{idx}] invalid source_tier: {rec.get('source_tier')}"
        conf = rec.get("confidence_score")
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            return False, f"record[{idx}] invalid confidence_score: {conf}"

    return True, "Schema validation checks passed."


def main() -> int:
    schema_path = SCHEMA_PATH
    data_path = DATA_PATH
    if len(sys.argv) >= 2:
        data_path = Path(sys.argv[1]).resolve()
    if len(sys.argv) >= 3:
        schema_path = Path(sys.argv[2]).resolve()

    ok, msg = validate(schema_path, data_path)
    if ok:
        print(f"PASS: {msg}")
        return 0
    print(f"FAIL: {msg}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
