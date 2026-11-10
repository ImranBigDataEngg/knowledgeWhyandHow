-- ANSI-style analytical patterns; adjust date/time functions for your SQL dialect.
-- Assumes orders(order_id, customer_id, order_date, amount, status).

-- Customer-level revenue, excluding cancelled/refunded orders.
SELECT customer_id,
       COUNT(*) AS completed_orders,
       SUM(amount) AS completed_revenue
FROM orders
WHERE status = 'completed'
GROUP BY customer_id;

-- Rank customers by completed revenue.
WITH totals AS (
    SELECT customer_id, SUM(amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT customer_id, revenue,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM totals;

-- Detect duplicate business keys.
SELECT order_id, COUNT(*) AS occurrences
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
