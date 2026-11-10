# Stage the batch in Azure and reconcile it in Databricks

Use Azure Data Factory (ADF) for file movement and orchestration. Let the Databricks notebook apply the lab's rules and return the reconciliation summary to ADF. ADF retains the staged CSV so a rejected `row_id` can be traced back to its source event.

## Run the notebook first

1. In an Azure Databricks workspace with Unity Catalog, use compute compatible with Unity Catalog volumes. Databricks Runtime 17.3 LTS uses Spark 4.0 and is a starting point for this lab. Give the notebook's run identity access to the notebook, compute, catalog, schema, and volume. The required Unity Catalog privileges for reading are `USE CATALOG`, `USE SCHEMA`, and `READ VOLUME`. [Runtime 17.3 LTS](https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/17.3lts) · [Volume permissions](https://learn.microsoft.com/en-us/azure/databricks/volumes/privileges).
2. Clone this repository into a Databricks Git folder. Open the [Databricks source notebook](../databricks_order_reconciliation.py) in the same directory as `spark_reconcile.py`. The Git folder makes the neighboring Python module importable. [Notebook source format](https://learn.microsoft.com/en-us/azure/databricks/notebooks/notebook-format) · [Workspace files](https://learn.microsoft.com/en-us/azure/databricks/files/workspace).
3. Upload [order_events.csv](../data/order_events.csv) into a test volume, for example at `/Volumes/<catalog>/<schema>/<volume>/manual/order_events.csv`. Uploading requires `WRITE VOLUME` in addition to the read privileges. Run the first cell to create the `input_path` widget, set it to the actual volume file path, and run all cells.
4. Compare the two displayed tables to [expected.json](../data/expected.json). The notebook exits with a JSON summary that includes `latest_orders = 5`, `rejected_rows = 6`, and `paid_cents = 3899`.

## Add the ADF pipeline

1. Create a landing container and a staging container in an ADLS Gen2 test storage account. Create an ADF ADLS Gen2 linked service that uses the factory's managed identity. At container scope, grant that identity Storage Blob Data Reader on landing and Storage Blob Data Contributor on staging. Upload the fixture as `incoming/lab-001/order_events.csv` in landing. [ADLS Gen2 connector](https://learn.microsoft.com/en-us/azure/data-factory/connector-azure-data-lake-storage#system-assigned-managed-identity-authentication).
2. Expose the staging prefix `abfss://staging@<account>.dfs.core.windows.net/orders/` as a Unity Catalog external volume. Use your workspace's storage credential and external location. Grant the Databricks run identity access to the volume separately from the ADF storage permissions. [External storage credentials](https://learn.microsoft.com/en-us/azure/databricks/connect/unity-catalog/cloud-storage/storage-credentials) · [Unity Catalog volumes](https://learn.microsoft.com/en-us/azure/databricks/volumes/).
3. Create a pipeline with a string parameter `batch_id`. Use `lab-001` for the first run. Add a Copy Data activity named `StageOrders` and configure two Binary datasets using the ADLS linked service. Set `order_events.csv` as the file name in both datasets. Define a String parameter `directory` on each dataset and set its folder path to `@dataset().directory`. Pass the following values from the Copy activity. [Dataset parameters](https://learn.microsoft.com/en-us/azure/data-factory/how-to-expression-language-functions).

   | Dataset | Container | Directory value in the pipeline |
   | --- | --- | --- |
   | Source | `landing` | `@concat('incoming/', pipeline().parameters.batch_id)` |
   | Sink | `staging` | `@concat('orders/', pipeline().parameters.batch_id)` |

4. Add a Databricks Notebook activity named `ReconcileOrders` on the success path of `StageOrders`. Configure an Azure Databricks linked service using your workspace's approved authentication and compute. Select the notebook using its workspace path. Under **Base parameters**, set `input_path` using the following dynamic expression with the actual catalog, schema, and volume names. [Compute linked service](https://learn.microsoft.com/en-us/azure/data-factory/compute-linked-services#azure-databricks-linked-service) · [Notebook activity](https://learn.microsoft.com/en-us/azure/data-factory/transform-data-databricks-notebook).

   ```text
   @concat('/Volumes/<catalog>/<schema>/<volume>/', pipeline().parameters.batch_id, '/order_events.csv')
   ```

5. Debug the pipeline. Inspect both activity outputs and compare the notebook's `runOutput` with the fixture summary. You can read the returned amount with `@activity('ReconcileOrders').output.runOutput.paid_cents` in a downstream expression.

For the retry exercise, rerun `lab-001` with the same source file after the first run completes. The Copy activity writes to the same batch path and the notebook computes the same result from that input. Use a new batch ID for different input data.
