# Why did the order totals change?

An order can appear several times in a batch. If you sum every paid event, a replay counts twice and a cancelled order can still contribute to the total. Reconcile the latest valid state of each order before counting what was paid.

## Input contract

[Order events](data/order_events.csv) is a UTF-8 CSV with the header `row_id,order_id,revision,status,amount_cents`. Each event occupies one CSV record on one line. The input uses standard double-quote escaping, exact column order, and signed 64-bit decimal integers or empty fields for the three numeric columns.

| Field | Meaning and validation |
| --- | --- |
| `row_id` | A stable source sequence, unique within the batch and in `1..999999`. An invalid or duplicated ID fails the batch because it cannot be audited or used as a tie-breaker. |
| `order_id` | A case-sensitive key. Trim surrounding ASCII spaces and reject the row if the key is empty. |
| `revision` | The order's business version, in `1..999999`. A later-arriving event can have an older revision. |
| `status` | One of `OPEN`, `PAID`, or `CANCELLED`, with exact case. |
| `amount_cents` | An integer in `0..1000000000`. Integer cents keep the aggregation exact. |

The Python loader checks the header, record width, numeric syntax, and IDs before processing. The Spark lab reads a conforming file with an explicit schema and validates source IDs before applying the business rules. [Spark CSV options](https://spark.apache.org/docs/4.0.3/sql-data-sources-csv.html).

## Reconciliation rule

1. Quarantine invalid events with `row_id` and the first applicable reason in this order. Use `missing_order_id`, then `invalid_revision`, then `invalid_status`, then `invalid_amount`. Keep the original file to look up the complete rejected record.
2. Among valid events, keep the highest `revision` per order. Use the highest `row_id` when revisions tie. Earlier valid events are superseded.
3. Count and sum the winners whose `status` is `PAID`. Include a paid order with zero cents in the count.

Compare the outcomes for three orders in the fixture.

| Order | Winning row | What the fixture demonstrates |
| --- | ---: | --- |
| `ORD-100` | 3 | A replay leaves one current row. Row 15 has a higher revision and is quarantined for its negative amount. |
| `ORD-200` | 5 | Cancellation wins over an earlier paid revision, so the order contributes zero to the paid total. |
| `ORD-300` | 8 | Two valid events share a revision. The higher source sequence selects the corrected amount of 2,600 cents. |

Check that `input_rows = rejected_rows + superseded_rows + latest_orders`. The fixture has `16 = 6 + 5 + 5` and a paid total of `1,299 + 2,600 + 0 = 3,899` cents. [Full expected JSON](data/expected.json).

## Run locally with Python or SQLite

Use Python 3.11 or later and run from the repository root. Pass `--input path/to/events.csv` to try a different batch.

```sh
python -m labs.order_reconciliation.reconcile --engine python
python -m labs.order_reconciliation.reconcile --engine sqlite
python -m unittest discover -s tests -p test_order_reconciliation.py -v
```

[Python implementation](reconcile.py) keeps a dictionary of winners and compares `(revision, row_id)` for each valid event. The SQLite engine loads the same typed records and runs [reconcile.sql](reconcile.sql). Its `ROW_NUMBER()` starts again per order and assigns position 1 to the winning row. [SQLite window functions](https://www.sqlite.org/windowfunctions.html).

## Run with PySpark

Use Python 3.11 or later and a JDK 17 or 21 with `JAVA_HOME` configured. The commands below use a POSIX shell from the repository root.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-spark.txt
python -m labs.order_reconciliation.reconcile --engine spark
python -m unittest discover -s tests -p test_spark_reconciliation.py -v
```

[Spark implementation](spark_reconcile.py) ranks the valid rows with `Window.partitionBy` and `row_number`. It collects full output only for this small local comparison. [PySpark installation](https://spark.apache.org/docs/4.0.3/api/python/getting_started/install.html) · [PySpark row_number](https://spark.apache.org/docs/4.0.3/api/python/reference/pyspark.sql/api/pyspark.sql.functions.row_number.html).

## Run with a managed or vendor tool

- [Azure Data Factory and Azure Databricks](guides/azure-databricks.md) use the same CSV and PySpark transformation.
- [Talend Studio 8](guides/talend.md) expresses the rule as a Standard Job.
- [Informatica Cloud Data Integration](guides/informatica.md) expresses the rule as a mapping.
