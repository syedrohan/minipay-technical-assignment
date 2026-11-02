
-- 1. Transaction count and total amount by status and day.
SELECT
    DATE(created_at) AS transaction_day,
    status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM transactions
GROUP BY DATE(created_at), status
ORDER BY transaction_day, status;


-- 2. Top 10 customers by successful transaction value.
SELECT
    c.id AS customer_id,
    c.customer_ref,
    c.name,
    COUNT(t.id) AS successful_transactions,
    ROUND(SUM(t.amount), 2) AS total_successful_value
FROM customers c
JOIN transactions t ON t.customer_id = c.id
WHERE t.status = 'SUCCESS'
GROUP BY c.id, c.customer_ref, c.name
ORDER BY total_successful_value DESC
LIMIT 10;


-- 3. Transactions stuck in PROCESSING for more than 15 minutes.
SELECT
    id,
    transaction_ref,
    customer_id,
    amount,
    status,
    created_at,
    ROUND(
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at)) / 60,
        2
    ) AS age_minutes
FROM transactions
WHERE status = 'PROCESSING'
  AND created_at < CURRENT_TIMESTAMP - INTERVAL '15 minutes'
ORDER BY created_at;


-- 4. Duplicate transaction references.
SELECT
    transaction_ref,
    COUNT(*) AS occurrence_count
FROM transactions
GROUP BY transaction_ref
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC, transaction_ref;


-- 5. Daily transaction success rate.
SELECT
    DATE(created_at) AS transaction_day,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_transactions,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'SUCCESS')
        / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate_percent
FROM transactions
GROUP BY DATE(created_at)
ORDER BY transaction_day;


-- 6. Reconciliation: successful transactions vs successful callbacks.
-- Count and value are based on distinct transactions, avoiding
-- double-counting a transaction if it has multiple callback records.
WITH successful_transactions AS (
    SELECT
        id,
        amount
    FROM transactions
    WHERE status = 'SUCCESS'
),
transactions_with_successful_callback AS (
    SELECT DISTINCT transaction_id
    FROM callbacks
    WHERE callback_status = 'SUCCESS'
),
callback_reconciliation AS (
    SELECT
        st.id,
        st.amount
    FROM successful_transactions st
    JOIN transactions_with_successful_callback c
        ON c.transaction_id = st.id
)
SELECT
    (SELECT COUNT(*) FROM successful_transactions)
        AS successful_transaction_count,
    (SELECT ROUND(COALESCE(SUM(amount), 0), 2)
     FROM successful_transactions)
        AS successful_transaction_value,
    (SELECT COUNT(*) FROM callback_reconciliation)
        AS transactions_with_successful_callback,
    (SELECT ROUND(COALESCE(SUM(amount), 0), 2)
     FROM callback_reconciliation)
        AS callback_success_value,
    (SELECT COUNT(*) FROM successful_transactions)
      - (SELECT COUNT(*) FROM callback_reconciliation)
        AS count_difference,
    (SELECT ROUND(COALESCE(SUM(amount), 0), 2)
     FROM successful_transactions)
      - (SELECT ROUND(COALESCE(SUM(amount), 0), 2)
         FROM callback_reconciliation)
        AS value_difference;


-- 7. Average and 95th percentile processing time in seconds.
-- Only completed transactions with both timestamps are considered.
SELECT
    COUNT(*) AS completed_transaction_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - created_at)))::numeric, 2)
        AS average_processing_seconds,
    ROUND(
        (PERCENTILE_CONT(0.95) WITHIN GROUP (
            ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))
        ))::numeric,
        2
    ) AS p95_processing_seconds
FROM transactions
WHERE completed_at IS NOT NULL
  AND completed_at >= created_at;
