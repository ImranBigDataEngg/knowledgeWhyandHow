# Data Engineering Interview Questions and Scenario Answers

## 1. Why choose CDC instead of full loads?

CDC captures inserts/updates/deletes incrementally, reducing read volume and latency. It introduces ordering, replay and delete-handling complexity. Full loads are simpler for small datasets.

## 2. How do you handle duplicate events?

Define a stable event ID or business key, deduplicate with deterministic ordering, and make writes idempotent. Track replayed and rejected rows.

## 3. Why is my Spark join slow?

Inspect physical plan, shuffle, data skew, file sizes and join cardinality. Consider filtering, pre-aggregation or broadcasting a small dimension after measuring.

## 4. What is the difference between partitioning and clustering?

Partitioning separates data into directory/table partitions, useful for coarse pruning. Clustering organizes data within or across files for selective access. Both depend on engine capabilities and workload.

## 5. How would you design a retry-safe ADF pipeline?

Use run IDs, stable source boundaries, staging, idempotent MERGE, dependency checks and alerting. Retrying should not duplicate data.

## 6. A source and target have equal row counts but different values. Next steps?

Compare keys, duplicates, nulls, checksums or aggregates, then perform keyed column-level reconciliation. Equal counts do not imply equality.

## 7. How do you implement SCD Type 2?

Maintain effective-from/effective-to timestamps, current-row indicator and a surrogate key. Close the previous version and insert a new version only when tracked attributes change.

## 8. Why choose Delta over plain Parquet?

Delta adds transactional table metadata and operations such as MERGE and version history. Plain Parquet is simpler for immutable files and broad interchange.

## 9. How do you secure Azure pipelines?

Prefer managed identity, least privilege, network restrictions, encrypted storage, secrets management, audit logs and nonproduction synthetic data.

## 10. What if a downstream team cannot find updated records?

Confirm environment, connection/database/schema, ingestion watermark, source key, transaction commit, replication lag and UI caching. Share a traceable test event and evidence at each boundary.
