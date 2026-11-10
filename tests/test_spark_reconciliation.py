import json
import tempfile
import unittest
from pathlib import Path

from labs.order_reconciliation.reconcile import FIXTURE
from labs.order_reconciliation.spark_reconcile import SCHEMA, collect_result, local_session, read_events, reconcile


class SparkReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = local_session()
        cls.addClassCleanup(cls.spark.stop)

    def test_matches_fixture(self):
        expected = json.loads(FIXTURE.with_name("expected.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "order events.csv"
            path.write_bytes(FIXTURE.read_bytes())
            self.assertEqual(collect_result(read_events(self.spark, path)), expected)

    def test_empty_batch(self):
        result = collect_result(self.spark.createDataFrame([], SCHEMA))
        self.assertEqual(result["latest"], [])
        self.assertEqual(result["rejected"], [])
        self.assertEqual(set(result["summary"].values()), {0})

    def test_duplicate_row_id_fails(self):
        rows = [(1, "ORD-1", 1, "PAID", 100), (1, "ORD-2", 1, "OPEN", 200)]
        with self.assertRaisesRegex(ValueError, "row_id must be unique"):
            reconcile(self.spark.createDataFrame(rows, SCHEMA))
