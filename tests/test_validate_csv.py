import csv
import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "examples" / "python" / "validate_csv.py"
spec = importlib.util.spec_from_file_location("validate_csv", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def test_counts_duplicates_and_missing_keys(tmp_path):
    path = tmp_path / "orders.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["order_id", "amount"])
        writer.writeheader()
        writer.writerows([
            {"order_id": "A", "amount": "10"},
            {"order_id": "A", "amount": "20"},
            {"order_id": "", "amount": "30"},
            {"order_id": "B", "amount": "40"},
        ])
    assert validator.validate_csv(str(path)) == {
        "rows": 4, "missing_key": 1, "duplicate_key": 1, "valid_key_rows": 2
    }


def test_missing_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("id,value\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="order_id"):
        validator.validate_csv(str(path))
