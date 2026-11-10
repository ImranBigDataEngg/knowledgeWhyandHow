"""Small reusable PySpark transformations; requires pyspark and a Spark runtime."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def latest_orders(df: DataFrame) -> DataFrame:
    """Keep latest event per order_id using a deterministic event_id tie-breaker."""
    window = Window.partitionBy("order_id").orderBy(
        F.col("updated_at").desc_nulls_last(),
        F.col("event_id").desc_nulls_last(),
    )
    return (
        df.filter(F.col("order_id").isNotNull())
        .withColumn("_rn", F.row_number().over(window))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def daily_revenue(df: DataFrame) -> DataFrame:
    """Aggregate completed orders by calendar date; amounts must be numeric."""
    return (
        df.filter(F.col("status") == "completed")
        .groupBy(F.to_date("order_date").alias("order_day"))
        .agg(F.sum("amount").alias("revenue"), F.count("*").alias("order_count"))
        .orderBy("order_day")
    )
