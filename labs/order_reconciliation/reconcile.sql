CREATE TABLE order_events (
    row_id INTEGER PRIMARY KEY CHECK (row_id BETWEEN 1 AND 999999),
    order_id TEXT,
    revision INTEGER,
    status TEXT,
    amount_cents INTEGER
);

CREATE VIEW classified_events AS
SELECT
    row_id, TRIM(order_id) AS order_id, revision, status, amount_cents,
    CASE
        WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 'missing_order_id'
        WHEN revision IS NULL OR revision NOT BETWEEN 1 AND 999999 THEN 'invalid_revision'
        WHEN status IS NULL OR status NOT IN ('OPEN', 'PAID', 'CANCELLED') THEN 'invalid_status'
        WHEN amount_cents IS NULL OR amount_cents NOT BETWEEN 0 AND 1000000000 THEN 'invalid_amount'
    END AS reason
FROM order_events;

CREATE VIEW rejected_events AS
SELECT row_id, reason
FROM classified_events
WHERE reason IS NOT NULL;

CREATE VIEW latest_orders AS
WITH ranked AS (
    SELECT
        row_id, order_id, revision, status, amount_cents,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY revision DESC, row_id DESC) AS position
    FROM classified_events
    WHERE reason IS NULL
)
SELECT row_id, order_id, revision, status, amount_cents
FROM ranked
WHERE position = 1;

CREATE VIEW reconciliation_summary AS
WITH source_counts AS (
    SELECT COUNT(*) AS input_rows, COUNT(reason) AS rejected_rows
    FROM classified_events
), current_counts AS (
    SELECT
        COUNT(*) AS latest_orders,
        COUNT(CASE WHEN status = 'PAID' THEN 1 END) AS paid_orders,
        COALESCE(SUM(CASE WHEN status = 'PAID' THEN amount_cents END), 0) AS paid_cents
    FROM latest_orders
)
SELECT
    input_rows, rejected_rows,
    input_rows - rejected_rows - latest_orders AS superseded_rows,
    latest_orders, paid_orders, paid_cents
FROM source_counts CROSS JOIN current_counts;
