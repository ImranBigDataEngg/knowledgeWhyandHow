"""Run the order reconciliation lab with Python, SQLite, or local Spark."""

import argparse
import csv
import json
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import NamedTuple

LAB = Path(__file__).resolve().parent
FIXTURE = LAB / "data" / "order_events.csv"
STATUSES = {"OPEN", "PAID", "CANCELLED"}
MAX_ID = 999_999
MAX_AMOUNT = 1_000_000_000


class Event(NamedTuple):
    row_id: int
    order_id: str
    revision: int | None
    status: str
    amount_cents: int | None


def optional_integer(value: str) -> int | None:
    if value == "":
        return None
    digits = value[1:] if value.startswith(("+", "-")) else value
    if not digits.isascii() or not digits.isdecimal():
        raise ValueError(f"expected an integer, found {value!r}")
    number = int(value)
    if not -(2**63) <= number < 2**63:
        raise ValueError(f"integer exceeds the signed 64-bit range: {value!r}")
    return number


def read_events(path: Path) -> list[Event]:
    events = []
    seen_ids = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        if next(reader, None) != list(Event._fields):
            raise ValueError(f"expected CSV header {','.join(Event._fields)}")
        for row in reader:
            if len(row) != len(Event._fields):
                raise ValueError(f"line {reader.line_num}: expected five fields")
            raw_id, order_id, raw_revision, status, raw_amount = row
            try:
                row_id = optional_integer(raw_id)
                if row_id is None or not 1 <= row_id <= MAX_ID or row_id in seen_ids:
                    raise ValueError("row_id must be unique and in 1..999999")
                event = Event(
                    row_id, order_id, optional_integer(raw_revision), status, optional_integer(raw_amount)
                )
            except ValueError as error:
                raise ValueError(f"line {reader.line_num}: {error}") from error
            seen_ids.add(row_id)
            events.append(event)
    return events


def reject_reason(event: Event) -> str | None:
    if not event.order_id:
        return "missing_order_id"
    if event.revision is None or not 1 <= event.revision <= MAX_ID:
        return "invalid_revision"
    if event.status not in STATUSES:
        return "invalid_status"
    if event.amount_cents is None or not 0 <= event.amount_cents <= MAX_AMOUNT:
        return "invalid_amount"
    return None


def reconcile_python(events: Sequence[Event]) -> dict:
    latest = {}
    rejected = []
    for event in events:
        event = event._replace(order_id=event.order_id.strip(" "))
        reason = reject_reason(event)
        if reason:
            rejected.append({"row_id": event.row_id, "reason": reason})
            continue

        previous = latest.get(event.order_id)
        if previous is None or (event.revision, event.row_id) > (previous.revision, previous.row_id):
            latest[event.order_id] = event

    current = [latest[order_id] for order_id in sorted(latest)]
    paid_amounts = [event.amount_cents for event in current if event.status == "PAID"]
    return {
        "latest": [event._asdict() for event in current],
        "rejected": sorted(rejected, key=lambda event: event["row_id"]),
        "summary": {
            "input_rows": len(events),
            "rejected_rows": len(rejected),
            "superseded_rows": len(events) - len(rejected) - len(current),
            "latest_orders": len(current),
            "paid_orders": len(paid_amounts),
            "paid_cents": sum(paid_amounts),
        },
    }


def reconcile_sqlite(events: Sequence[Event]) -> dict:
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        database.executescript((LAB / "reconcile.sql").read_text(encoding="utf-8"))
        database.executemany("INSERT INTO order_events VALUES (?, ?, ?, ?, ?)", events)
        return {
            "latest": [dict(row) for row in database.execute("SELECT * FROM latest_orders ORDER BY order_id")],
            "rejected": [dict(row) for row in database.execute("SELECT * FROM rejected_events ORDER BY row_id")],
            "summary": dict(database.execute("SELECT * FROM reconciliation_summary").fetchone()),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("python", "sqlite", "spark"), default="python")
    parser.add_argument("--input", type=Path, default=FIXTURE, help="Input CSV, defaults to the lab fixture")
    args = parser.parse_args()

    if args.engine == "spark":
        from .spark_reconcile import collect_result, local_session
        from .spark_reconcile import read_events as read_spark_events

        spark = local_session()
        try:
            result = collect_result(read_spark_events(spark, args.input))
        finally:
            spark.stop()
    else:
        run = reconcile_python if args.engine == "python" else reconcile_sqlite
        result = run(read_events(args.input))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
