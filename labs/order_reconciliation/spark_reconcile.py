"""Apply the order reconciliation contract to a Spark DataFrame."""

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

SCHEMA = "row_id BIGINT, order_id STRING, revision BIGINT, status STRING, amount_cents BIGINT"


def local_session() -> SparkSession:
    spark = (
        SparkSession.builder.master("local[2]").appName("order-reconciliation")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_events(spark: SparkSession, path: str | Path) -> DataFrame:
    if isinstance(path, Path):
        path = path.resolve().as_posix()
    return (
        spark.read.schema(SCHEMA)
        .option("header", True)
        .option("enforceSchema", False)
        .option("mode", "FAILFAST")
        .option("escape", '"')
        .csv(path)
    )


def reconcile(events: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]:
    row_id = F.col("row_id")
    invalid_ids = (
        events.groupBy("row_id").count()
        .where(row_id.isNull() | ~row_id.between(1, 999_999) | (F.col("count") > 1))
        .take(1)
    )
    if invalid_ids:
        raise ValueError("row_id must be unique and in 1..999999")

    order_id = F.col("order_id")
    revision = F.col("revision")
    status = F.col("status")
    amount = F.col("amount_cents")
    classified = events.withColumn("order_id", F.trim(order_id)).withColumn(
        "reason",
        F.when(order_id.isNull() | (order_id == ""), "missing_order_id")
        .when(revision.isNull() | ~revision.between(1, 999_999), "invalid_revision")
        .when(status.isNull() | ~status.isin("OPEN", "PAID", "CANCELLED"), "invalid_status")
        .when(amount.isNull() | ~amount.between(0, 1_000_000_000), "invalid_amount"),
    )
    rejected = classified.where(F.col("reason").isNotNull()).select("row_id", "reason")
    order_window = Window.partitionBy("order_id").orderBy(F.desc("revision"), F.desc("row_id"))
    latest = (
        classified.where(F.col("reason").isNull())
        .withColumn("position", F.row_number().over(order_window))
        .where(F.col("position") == 1)
        .drop("position", "reason")
    )

    source_counts = classified.agg(
        F.count("*").alias("input_rows"), F.count("reason").alias("rejected_rows")
    )
    is_paid = status == "PAID"
    current_counts = latest.agg(
        F.count("*").alias("latest_orders"),
        F.count(F.when(is_paid, 1)).alias("paid_orders"),
        F.coalesce(F.sum(F.when(is_paid, amount)), F.lit(0)).alias("paid_cents"),
    )
    summary = source_counts.crossJoin(current_counts).withColumn(
        "superseded_rows", F.col("input_rows") - F.col("rejected_rows") - F.col("latest_orders")
    )
    return latest, rejected, summary


def collect_result(events: DataFrame) -> dict:
    """Collect the small lab result for comparison with the golden fixture."""
    latest, rejected, summary = reconcile(events)
    return {
        "latest": [row.asDict() for row in latest.orderBy("order_id").collect()],
        "rejected": [row.asDict() for row in rejected.orderBy("row_id").collect()],
        "summary": summary.first().asDict(),
    }
