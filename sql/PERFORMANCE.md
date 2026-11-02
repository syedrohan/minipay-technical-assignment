# SQL Performance Analysis

## Objective
Measure the performance of transaction lookup before and after adding a composite index.

## Test environment
- Database: PostgreSQL 16 (GitHub Actions)
- Dataset: 50,000 transactions
- Lookup reference: `TXN00012345`
- Query: Find the latest transaction matching the reference.

## Query
```sql
SELECT id, transaction_ref, customer_id, amount, status, created_at
FROM transactions
WHERE transaction_ref = 'TXN00012345'
ORDER BY id DESC
LIMIT 1;
```

## Optimization
Created a composite index:

```sql
CREATE INDEX IF NOT EXISTS idx_transactions_ref_id
ON transactions (transaction_ref, id DESC);
```

The index supports filtering by `transaction_ref` and retrieving the latest matching record by descending `id`.

## Benchmark results

| Metric | Before index | After index |
|---|---:|---:|
| Execution time | 3.229 ms | 0.045 ms |
| Scan method | Sequential Scan | Index Scan |
| Rows removed by filter | 49,999 | Not applicable |
| Shared buffer activity | 616 hits | 1 hit, 3 reads |
| Separate sort operation | Yes | No |

**Execution time improvement:** Approximately 71.8× faster, representing a 98.6% reduction in execution time.

## Execution plan observations

### Before index
- PostgreSQL performed a sequential scan across the transactions table.
- It removed 49,999 rows while searching for the requested reference.
- It performed a separate sort on `id DESC`.
- Execution time was 3.229 ms.

### After index
- PostgreSQL used `idx_transactions_ref_id`.
- The index scan located the matching transaction directly.
- The separate sort operation was eliminated.
- Execution time decreased to 0.045 ms.

## Conclusion
The composite index substantially improved the transaction lookup performance on the 50,000-row test dataset. It reduced execution time from 3.229 ms to 0.045 ms.

These results represent the measured GitHub Actions benchmark run. Execution times may vary across environments and repeated runs. The index should also be evaluated against write overhead and storage requirements before production deployment.
