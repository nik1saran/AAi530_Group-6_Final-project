import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "person1" / "verified-crisis-batch.schema.json"
DATA_PATH = ROOT / "data" / "person1" / "sample-validated-output.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    required_batch = schema["required"]
    missing_batch = [k for k in required_batch if k not in data]
    if missing_batch:
        print(f"FAIL: Missing batch fields: {missing_batch}")
        return 1

    record_schema = schema["properties"]["records"]["items"]
    required_record = record_schema["required"]
    enum_status = set(record_schema["properties"]["status"]["enum"])
    enum_tier = set(record_schema["properties"]["source_tier"]["enum"])

    for idx, rec in enumerate(data.get("records", []), start=1):
        missing = [k for k in required_record if k not in rec]
        if missing:
            print(f"FAIL: record[{idx}] missing required fields: {missing}")
            return 1
        if rec.get("status") not in enum_status:
            print(f"FAIL: record[{idx}] invalid status: {rec.get('status')}")
            return 1
        if rec.get("source_tier") not in enum_tier:
            print(f"FAIL: record[{idx}] invalid source_tier: {rec.get('source_tier')}")
            return 1
        conf = rec.get("confidence_score")
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            print(f"FAIL: record[{idx}] invalid confidence_score: {conf}")
            return 1

    print("PASS: Schema validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

