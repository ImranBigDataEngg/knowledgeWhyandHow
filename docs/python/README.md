# Python for Data Engineering

## Why Python?

Python is useful for API ingestion, validation, orchestration, metadata operations and testable ETL utilities. For very large transformations, prefer a distributed execution engine rather than loading everything into local memory.

## Engineering patterns

- Stream large CSV files with `csv.DictReader` rather than reading the entire file.
- Validate contracts explicitly: required columns, nulls, data types and uniqueness.
- Use `logging`, structured errors, bounded retries and timeouts.
- Separate pure transformation functions from I/O for easier unit tests.
- Read credentials from an approved secret manager or environment, never source code.
- Track schema version, input file, run ID and row counts for auditability.

Try the [CSV validator](../../examples/python/validate_csv.py).
