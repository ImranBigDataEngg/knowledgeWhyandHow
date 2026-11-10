import json
import tempfile
import unittest
from pathlib import Path

from labs.order_reconciliation.reconcile import FIXTURE, read_events, reconcile_python, reconcile_sqlite

ENGINES = (reconcile_python, reconcile_sqlite)


class LocalReconciliationTests(unittest.TestCase):
    def test_matches_fixture_in_either_input_order(self):
        events = read_events(FIXTURE)
        expected = json.loads(FIXTURE.with_name("expected.json").read_text(encoding="utf-8"))
        for engine in ENGINES:
            for batch in (events, events[::-1]):
                with self.subTest(engine=engine.__name__, first_row=batch[0].row_id):
                    self.assertEqual(engine(batch), expected)

    def test_empty_and_rejected_only_batches(self):
        invalid = next(event for event in read_events(FIXTURE) if event.row_id == 9)
        for engine in ENGINES:
            for batch in ([], [invalid]):
                with self.subTest(engine=engine.__name__, input_rows=len(batch)):
                    result = engine(batch)
                    self.assertEqual(result["latest"], [])
                    self.assertEqual(result["summary"], {
                        "input_rows": len(batch), "rejected_rows": len(batch), "superseded_rows": 0,
                        "latest_orders": 0, "paid_orders": 0, "paid_cents": 0,
                    })

    def test_malformed_csv_fails_at_ingestion(self):
        header = "row_id,order_id,revision,status,amount_cents\n"
        bad_batches = {
            "wrong header": "id,order,revision,status,amount\n",
            "extra field": header + "1,ORD-1,1,PAID,300,extra\n",
            "duplicate id": header + "1,ORD-1,1,PAID,300\n1,ORD-2,1,OPEN,400\n",
            "missing id": header + ",ORD-1,1,PAID,300\n",
            "out-of-range id": header + "1000000,ORD-1,1,PAID,300\n",
            "non-integer amount": header + "1,ORD-1,1,PAID,3.00\n",
            "integer overflow": header + "1,ORD-1,1,PAID,9223372036854775808\n",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            for name, batch in bad_batches.items():
                with self.subTest(case=name):
                    path.write_text(batch, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        read_events(path)
