"""Streaming CSV validation with basic quality metrics (standard library only)."""
import argparse
import csv
import json
from pathlib import Path


def validate_csv(path: str, key_column: str = "order_id") -> dict:
    """Return counts for rows with missing or duplicate business keys."""
    seen = set()
    result = {"rows": 0, "missing_key": 0, "duplicate_key": 0}
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or key_column not in reader.fieldnames:
            raise ValueError(f"CSV must contain column {key_column!r}")
        for row in reader:
            result["rows"] += 1
            key = (row.get(key_column) or "").strip()
            if not key:
                result["missing_key"] += 1
            elif key in seen:
                result["duplicate_key"] += 1
            else:
                seen.add(key)
    result["valid_key_rows"] = result["rows"] - result["missing_key"] - result["duplicate_key"]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check missing and duplicate CSV keys")
    parser.add_argument("csv_path")
    parser.add_argument("--key", default="order_id")
    args = parser.parse_args()
    print(json.dumps(validate_csv(args.csv_path, args.key), indent=2))
