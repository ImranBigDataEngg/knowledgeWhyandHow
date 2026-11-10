# Legacy ETL to Modern Data Platform: Migration Playbook

## Discover

Inventory Talend/Informatica jobs, schedules, sources, target schemas, dependencies, SQL overrides, custom code, SLAs, secrets and operational runbooks.

## Classify

Group jobs into direct copy, joins/lookups, aggregations, CDC, SCD, file handling and complex business logic. Prioritize by risk and value.

## Translate

Map each source transformation to documented SQL or PySpark semantics. Verify differences in null comparison, collation, decimal precision, timestamp timezone, error handling and transaction boundaries.

## Validate

Run source and target in parallel using synthetic or approved test data. Compare row counts, key sets, duplicates, null counts, control totals and column-level values. Record accepted differences.

## Cut over

Define rollback, ownership, monitoring, reconciliation thresholds and a freeze window. Never disable the legacy process until recovery and sign-off are documented.
