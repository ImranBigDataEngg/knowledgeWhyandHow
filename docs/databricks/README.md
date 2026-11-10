# Databricks and Delta Lake

## Why a lakehouse?

A lakehouse keeps low-cost lake storage while adding table metadata, transactions and governance patterns associated with warehouses. Delta Lake provides ACID transactions, schema enforcement and time travel (subject to retention).

## Common operations

```sql
CREATE TABLE IF NOT EXISTS orders (order_id BIGINT, amount DECIMAL(12,2)) USING DELTA;
MERGE INTO orders AS target
USING staged_orders AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET amount = source.amount
WHEN NOT MATCHED THEN INSERT (order_id, amount) VALUES (source.order_id, source.amount);
```

`staged_orders` must exist and be deduplicated by `order_id` before this MERGE. A source containing multiple matches for one target can cause ambiguous updates.

## Optimization decisions

- Inspect the query plan before tuning; avoid guessing bottlenecks.
- Partition only when access patterns and table size justify it; excessive small partitions create file overhead.
- Compact small files and use clustering/optimization features supported by your platform version.
- Cache only reused data when memory trade-offs justify it.
- Manage checkpoint, schema evolution, retention and VACUUM policies carefully.

**Interview scenario:** Daily job slows as input grows. Measure scan size, skew, shuffle bytes, spill, file counts and join strategy before increasing compute.
