# Incident 001 — Intermittent Payment Search HTTP 500

## 1. Incident Summary

**Incident ID:** INC-001  
**Component:** MiniPay Payment Search API  
**Endpoint:** `GET /api/payments/search/{transaction_ref}`  
**Reported Symptom:** Intermittent HTTP 500 errors during payment searches  
**Investigation Status:** Reproduced through a simulated database exception  
**Severity:** High (assessment scenario)

The payment search endpoint retrieves the latest payment matching a transaction reference. A database failure during the search could cause an unhandled exception and return HTTP 500.

## 2. Investigation

The following areas were reviewed:

- Payment search route implementation.
- Database session and SQLAlchemy query execution.
- Transaction reference matching and duplicate-reference handling.
- API behavior when a transaction does not exist.
- Database exception handling.

A controlled database exception was introduced in an automated test to verify the endpoint's failure behavior.

## 3. Root Cause

The search operation did not initially handle SQLAlchemy database exceptions.

When the database query failed, the exception could propagate through the API request and result in an HTTP 500 response instead of a controlled service-unavailable response.

**Note:** This was a simulated failure for assessment purposes. No actual production database outage was reproduced.

## 4. Corrective Actions

The following changes were implemented:

1. Added SQLAlchemy database exception handling to the payment search route.
2. Converted database query failures into HTTP 503 Service Unavailable responses.
3. Added a consistent error message: `Payment search is temporarily unavailable`.
4. Preserved HTTP 404 behavior when a transaction reference does not exist.
5. Removed a duplicate route decorator.

## 5. Validation and Test Evidence

Automated API tests cover:

| Test scenario | Expected result |
|---|---|
| Search existing transaction reference | HTTP 200 |
| Search unknown transaction reference | HTTP 404 |
| Search duplicate transaction reference | Latest matching payment returned |
| Simulated database exception | HTTP 503 |

The API test suite reported 18 passing tests before the new failure-handling test was added. The new database-failure test subsequently passed in GitHub Actions.

## 6. Preventive Measures

- Handle database exceptions explicitly in API endpoints.
- Monitor HTTP 5xx response rates.
- Review application logs for recurring database connectivity errors.
- Include database failure scenarios in automated API testing.
- Monitor database availability and connection health.

## 7. Final Outcome

The payment search endpoint now returns a controlled HTTP 503 response when a SQLAlchemy database exception occurs, rather than allowing that exception to propagate as an unhandled server error.

**Validation limitation:** The failure scenario was simulated in CI. No live production incident or production recovery was verified.
