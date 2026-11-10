# Azure Data Engineering — Why and How

## Core building blocks

- **Azure Data Lake Storage Gen2:** durable object storage; hierarchical namespaces support directory-oriented analytics workflows.
- **Azure Data Factory:** schedules and orchestrates pipelines, copy activities and dependencies; it is not a replacement for distributed transformation engines.
- **Azure Databricks:** managed Spark for batch and streaming transformations.
- **Azure SQL Database / Synapse / Fabric:** serving and analytics options with different performance, governance and cost trade-offs.
- **Microsoft Entra ID and managed identities:** authenticate without embedding secrets in notebooks.
- **Azure Key Vault:** centralize secret lifecycle where needed.

## Reference flow

`Source systems → ingestion (ADF) → ADLS bronze → Databricks silver → Delta gold → BI / APIs`

**Why separate layers?** Raw retention improves replayability; validated silver tables make business rules explicit; curated gold tables serve consumers.

## Production checklist

1. Define source contracts, ownership, SLAs and late-arriving-data handling.
2. Choose incremental ingestion with a durable watermark or CDC, rather than full refresh by default.
3. Use managed identity / least-privilege access and private networking where required.
4. Make writes idempotent and add data-quality checks before publishing.
5. Monitor freshness, record counts, costs, pipeline failures and schema drift.
6. Define disaster recovery, retention, encryption and audit requirements.

**Interview scenario:** ADF pipeline reruns duplicate records. Explain a deterministic business key, staging tables, transactional MERGE, and an ingestion-run audit log.
