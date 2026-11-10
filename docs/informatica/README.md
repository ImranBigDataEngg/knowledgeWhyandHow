# Informatica ETL — Why and How

Informatica mappings model source-to-target data flow. Component and deployment details vary across PowerCenter and cloud services.

## Key concepts

- **Source / target definitions:** data contracts and metadata.
- **Expression transformation:** column-level rules and derived fields.
- **Lookup:** enrichment from reference data; choose caching carefully.
- **Aggregator:** grouped metrics; ensure correct grouping and sorting assumptions.
- **Router / Filter:** conditional row paths.
- **Workflow / task orchestration:** dependency management, scheduling and restart behavior.

## Reliability checklist

1. Define source-to-target mapping and transformation rule ownership.
2. Check null handling, data types, precision and rejected rows.
3. Test inserts, updates, duplicates, deletes and late arrivals.
4. Compare row counts and control totals at every stage.
5. Keep parameter files and credentials out of source control.

**Interview scenario:** Target totals differ from source totals. Reconcile filters, lookup multiplicity, rejected records, truncation and incremental boundaries.
