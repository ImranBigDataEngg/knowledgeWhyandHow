# Knowledge Why and How

An open-source data engineering knowledge base with short guides, runnable examples, and synthetic data. Each lab starts with a practical question, explains the rule, and shows how to verify the answer.

## Learning tracks

| Topic | Start here |
| --- | --- |
| Azure Data Engineering | [Storage, orchestration, and ingestion](docs/azure/README.md) |
| Databricks | [Lakehouse and Delta Lake](docs/databricks/README.md) |
| PySpark | [Execution, shuffles, and reliability](docs/pyspark/README.md) |
| Python | [ETL and input validation](docs/python/README.md) |
| SQL | [Joins, window functions, and incremental loads](docs/sql/README.md) |
| Talend | [Standard Job design](docs/talend/README.md) |
| Informatica | [Mapping design and reconciliation](docs/informatica/README.md) |

## Lab 01 · Why did the order totals change?

An orders feed arrives with late records, replayed revisions, cancellations, and invalid amounts. Use Python, SQLite, or PySpark to find each order's latest valid state, quarantine invalid records, and reconcile the paid total. The lab includes walkthroughs for Azure Data Factory, Databricks, Talend, and Informatica. [Open the lab](labs/order_reconciliation/README.md).

## Quick start

From the repository root with Python 3.11 or later, run either engine on the bundled dataset. Both use the Python standard library.

```sh
python -m labs.order_reconciliation.reconcile --engine python
python -m labs.order_reconciliation.reconcile --engine sqlite
python -m unittest discover -s tests -p test_order_reconciliation.py -v
```

The sample yields **5 current orders**, **6 rejected rows**, and **3,899 cents across 3 paid orders**. The [expected result](labs/order_reconciliation/data/expected.json) includes each winning row and reject reason. For Spark setup, follow the [local PySpark instructions](labs/order_reconciliation/README.md#run-with-pyspark).

With a JDK 17 or 21 configured, run the full test suite in a virtual environment.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## More practice

- [CSV quality checker](examples/python/validate_csv.py)
- [PySpark transformations](examples/pyspark/transformations.py)
- [SQL analytics](examples/sql/analytics.sql)
- [Medallion pipeline project specification](projects/medallion-pipeline/README.md)
- [ETL migration playbook](guides/etl-migration.md)
- [Scenario-based interview practice](interview/scenarios.md)

## Contribute

New labs, SQL dialect ports, and reproducible bug reports are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for starter tasks and the verification steps. This project uses the [MIT License](LICENSE).
