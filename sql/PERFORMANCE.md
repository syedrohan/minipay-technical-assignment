# MiniPay SQL Performance Investigation

## 1. Objective

Investigate the performance of transaction searches using the `transaction_ref` column in the PostgreSQL transactions table.

The synthetic dataset contains 50,000 transactions. The objective is to compare the lookup performance before and after introducing an appropriate database index.

## 2. Problem Identified

The original database schema does not define an index on `transactions.transaction_ref`.

The support CLI searches transactions using the following pattern:

```sql
SELECT id, transaction_ref, customer_id, amount, status, created_at
FROM transactions
WHERE transaction_ref = 'TXN00012345'
ORDER BY id DESC
LIMIT 1;
```

Without a suitable index, PostgreSQL may need to scan a large portion of the transactions table to locate matching records.

## 3. Proposed Optimization

The following composite index was introduced:

```sql
CREATE INDEX IF NOT EXISTS idx_transactions_ref_id
ON transactions (transaction_ref, id DESC);
```

The index supports filtering by transaction reference and retrieving the latest matching record by descending ID.

## 4. Benchmark Method

The benchmark is defined in `sql/performance_test.sql`.

It performs the following steps:

1. Refreshes PostgreSQL statistics using `ANALYZE`.
2. Executes the transaction lookup before creating the index.
3. Captures the execution plan using `EXPLAIN (ANALYZE, BUFFERS)`.
4. Creates the composite index.
5. Refreshes statistics again.
6. Executes the same lookup and captures the optimized execution plan.

## 5. Results

**Execution evidence: pending.**

The benchmark must be executed against the seeded PostgreSQL database before recording actual execution times or claiming a performance improvement.

| Metric | Before index | After index |
|---|---|---|
| Execution time | Pending measurement | Pending measurement |
| Scan method | Pending observation | Pending observation |
| Buffer activity | Pending measurement | Pending measurement |

## 6. Expected Outcome

The index is expected to reduce the work required for transaction-reference lookups.

However, PostgreSQL's query planner determines whether to use the index based on table statistics and estimated query cost. Actual execution plans and timings will determine whether the optimization is beneficial.

## 7. Conclusion

The proposed index targets the transaction-search access pattern used by the MiniPay support CLI. Final conclusions will be added after collecting and comparing actual PostgreSQL execution evidence.
