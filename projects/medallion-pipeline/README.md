# Portfolio Project: Medallion Orders Pipeline

## Objective

Build an auditable pipeline from synthetic order events into curated revenue metrics.

## Architecture

`CSV/API → Bronze (raw events) → Silver (validated/deduplicated) → Gold (daily revenue)`

## Synthetic schema

`order_id,customer_id,order_date,amount,status,updated_at,event_id`

## Implementation milestones

1. Generate synthetic input containing duplicates, null IDs, late updates and malformed amounts.
2. Ingest to Bronze with source filename, ingestion timestamp and run ID.
3. Validate and quarantine invalid records; publish Silver using latest `updated_at` plus `event_id` as tie-breaker.
4. Upsert into a Delta Silver table using an idempotent MERGE.
5. Build Gold revenue by date and status, documenting cancellation/refund semantics.
6. Add tests for replay, schema drift, duplicates and empty input.
7. Monitor latency, counts, freshness and cost per successful run.

## Acceptance criteria

- Reprocessing the same batch does not double-count orders.
- Invalid records are counted and traceable.
- Gold totals reconcile to eligible Silver records.
- Late updates are reflected after reruns.

## Deliverables

Architecture diagram, data dictionary, test evidence, failure/retry runbook and cost estimate. This is a project specification; cloud resources and Delta tables are not provisioned by this repository.
