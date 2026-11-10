# Talend ETL — Why and How

Talend Studio jobs connect components to implement ingestion, transformations and outputs. Exact features depend on Talend edition and version.

## Typical flow

`tFileInputDelimited → tMap → tFilterRow → tDBOutput`

- **tMap:** mappings, lookups, expressions and filtering.
- **Context variables:** externalize environment-specific configuration; never store passwords in a public repository.
- **Reject flows:** route invalid records to a controlled quarantine destination.
- **Joblets / reusable jobs:** share common patterns while keeping ownership clear.

## Operational considerations

Document schema contracts, lookup join behavior, batch/commit sizes, restartability and error-handling. For migrations, inventory custom Java expressions, dependencies and job scheduling before rebuilding pipelines.

**Interview scenario:** A lookup multiplies records unexpectedly. Verify key uniqueness and join semantics in `tMap` and reconcile counts at each component boundary.
