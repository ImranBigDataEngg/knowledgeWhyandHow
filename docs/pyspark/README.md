# PySpark: Execution, Shuffles and Reliability

## Why Spark?

Spark processes datasets in parallel across executors. Transformations such as `select`, `filter`, and `groupBy` are lazy; an action such as `count` or `write` triggers execution.

## Narrow versus wide transformations

- **Narrow:** `filter` and many `select` operations can process each partition independently.
- **Wide:** `groupBy`, `distinct` and many joins may require a network shuffle.

## Practical rules

1. Select only needed columns and filter early.
2. Prefer built-in functions over Python UDFs where possible.
3. Examine `explain()` and Spark UI stages, tasks, skew and spill.
4. Broadcast only genuinely small lookup tables when memory allows.
5. Avoid `collect()` on large datasets; it moves data to the driver.
6. Make event-time and timezone assumptions explicit.

## Example

See [transformations.py](../../examples/pyspark/transformations.py) for a reusable cleaning and aggregation example.

**Interview scenario:** One Spark task takes 20 minutes while others take seconds. Investigate skewed join/group keys and consider salting, pre-aggregation or an alternate join plan.
