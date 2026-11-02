
-- MiniPay transaction lookup performance investigation.
-- Run against a freshly seeded database.

-- Update PostgreSQL statistics before measuring.
ANALYZE transactions;

-- 1. Baseline: transaction lookup without the new index.
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id,
    transaction_ref,
    customer_id,
    amount,
    status,
    created_at
FROM transactions
WHERE transaction_ref = 'TXN00012345'
ORDER BY id DESC
LIMIT 1;


-- 2. Add an index for transaction reference lookups.
CREATE INDEX IF NOT EXISTS idx_transactions_ref_id
ON transactions (transaction_ref, id DESC);


-- 3. Refresh statistics after creating the index.
ANALYZE transactions;

-- 4. Optimized: repeat exactly the same lookup.
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id,
    transaction_ref,
    customer_id,
    amount,
    status,
    created_at
FROM transactions
WHERE transaction_ref = 'TXN00012345'
ORDER BY id DESC
LIMIT 1;
