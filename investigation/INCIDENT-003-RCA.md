# Incident 003 – Slow Transaction Search

## 1. Incident Summary

**Incident:** Slow transaction search  
**Area:** Payment API / PostgreSQL  
**Scenario:** Transaction searches become slower as the database grows.

This investigation uses the MiniPay CI benchmark dataset containing 50,000 transactions. It is a controlled performance test, not a reproduced production incident.

## 2. Investigation

The original search query filtered transactions by `transaction_ref`, sorted the results by descending ID, and returned the latest matching record.

The initial execution plan showed:
- Sequential Scan on the transactions table.
- 49,999 rows removed by the filter.
- A Sort operation was required.
- Execution time: 3.229 ms.

## 3. Root Cause

The query did not have a suitable index supporting both the transaction reference filter and descending ID ordering.

As a result, PostgreSQL scanned the table and sorted matching results.

## 4. Corrective Action

Created a composite index:

```sql
CREATE INDEX IF NOT EXISTS idx_transactions_ref_id
ON transactions (transaction_ref, id DESC);
```

This allows PostgreSQL to locate matching transaction references and retrieve the latest record more efficiently.

## 5. Performance Results

| Metric | Before | After |
|---|---:|---:|
| Execution time | 3.229 ms | 0.045 ms |
| Query plan | Sequential Scan + Sort | Index Scan |
| Rows removed by filter | 49,999 | Not applicable |
| Shared buffer activity | 616 hits | 1 hit, 3 reads |

**Measured improvement:** Approximately 71.8× faster, with a 98.6% reduction in execution time.

## 6. Validation

The benchmark was executed against PostgreSQL 16 in GitHub Actions using 50,000 generated transactions.

The execution plans and timing results were captured in the SQL performance test artifact.

## 7. Preventive Measures

- Add indexes based on frequently used query filters and sorting.
- Review execution plans for slow queries.
- Monitor query latency as transaction volume increases.
- Include database performance checks in CI.

## 8. Limitations

These results represent a controlled CI benchmark. Actual production performance may vary depending on hardware, database configuration, cache state, and data volume. No live production incident was reproduced.
