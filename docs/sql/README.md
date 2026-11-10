# SQL for Data Engineers

## Why SQL matters

SQL defines transformations, validations, reconciliation and analytical models across databases and lakehouse engines. Always check the target dialect: SQL Server, Sybase, Spark SQL and PostgreSQL differ.

## Core patterns

- **Joins:** validate join cardinality; a many-to-many join can multiply rows.
- **Window functions:** rank or deduplicate without collapsing detail rows.
- **CTEs:** improve query readability, but are not necessarily materialized.
- **Incremental loads:** compare high-watermark and CDC approaches; plan for late updates.
- **Transactions:** make related updates atomic when the engine supports them.

## Duplicate check

```sql
SELECT business_key, COUNT(*) AS duplicate_count
FROM staging_table
GROUP BY business_key
HAVING COUNT(*) > 1;
```

## Latest row per business key

```sql
WITH ranked AS (
  SELECT t.*,
         ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY updated_at DESC, event_id DESC) AS rn
  FROM staging_table t
)
SELECT * FROM ranked WHERE rn = 1;
```

Include a deterministic tie-breaker, such as a unique `event_id`. See [analytics.sql](../../examples/sql/analytics.sql).
