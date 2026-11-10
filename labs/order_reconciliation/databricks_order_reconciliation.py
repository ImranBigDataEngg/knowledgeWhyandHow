# Databricks notebook source
import json

from spark_reconcile import read_events, reconcile

dbutils.widgets.text("input_path", "")

# COMMAND ----------

input_path = dbutils.widgets.get("input_path")
if not input_path.startswith("/Volumes/"):
    raise ValueError("Set input_path to the fixture CSV under /Volumes/<catalog>/<schema>/<volume>/")

latest, rejected, summary = reconcile(read_events(spark, input_path))
display(latest.orderBy("order_id"))
display(rejected.orderBy("row_id"))
display(summary)

# COMMAND ----------

dbutils.notebook.exit(json.dumps(summary.first().asDict(), sort_keys=True))
