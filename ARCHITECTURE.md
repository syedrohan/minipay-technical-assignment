# MiniPay Architecture

## 1. Overview

MiniPay follows a layered application architecture consisting of a browser-based user interface, REST API, business logic, database access layer, and PostgreSQL database.

The application is developed using FastAPI and SQLAlchemy, with PostgreSQL for persistent transaction data.

## 2. High-Level Architecture

```text
             User / Merchant
                    |
                    v
          Browser Dashboard / Client
                    |
                    v
              FastAPI API
                    |
          +---------+---------+
          |                   |
          v                   v
     API Routes          Authentication
          |
          v
     Business Services
          |
          v
      SQLAlchemy ORM
          |
          v
       PostgreSQL
          |
          +----------------------+
          |                      |
          v                      v
      Transactions           Callbacks
```

## 3. Application Components

### User Interface

Location: `application/ui/`

The browser dashboard provides:

- API-key input.
- Customer creation.
- Payment submission.
- Payment lookup.
- API response and error display.

The interface communicates with the backend using HTTP requests.

### API Layer

Location: `application/api/`

The FastAPI application exposes REST endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/customers` | Create a customer |
| POST | `/api/payments` | Submit a payment |
| GET | `/api/payments/{id}` | Retrieve payment by ID |
| GET | `/api/customers/{id}/payments` | Retrieve customer payments |
| GET | `/api/payments/search/{transaction_ref}` | Search by transaction reference |
| GET | `/health` | Check application and database health |

Merchant endpoints require API-key authentication through the `X-API-Key` header.

### Authentication

Location: `application/api/auth.py`

The API validates the merchant API key using the `MINIPAY_API_KEY` environment variable.

Invalid or missing credentials are rejected. The health endpoint remains publicly accessible.

### Business Logic

Location: `application/api/services.py`

The service layer handles customer and payment creation, validates customer existence, checks duplicate transaction references, and persists transaction records.

### Database Layer

Locations:

- `application/api/database.py`
- `application/api/models.py`
- `sql/schema.sql`

SQLAlchemy manages database connections and ORM operations.

PostgreSQL stores:

- Customers.
- Transactions.
- Callback attempts.

Transaction references are not unique in the supplied schema, so search operations return the latest matching transaction by ID.

## 4. Python Support CLI

Location: `python/support_tool.py`

The CLI connects directly to PostgreSQL using the configured `DATABASE_URL`.

It retrieves transaction, customer, and callback information and identifies potential anomalies such as:

- Long-running PROCESSING transactions.
- Failed transactions.
- Failed callback attempts.
- Successful payments without a successful callback.

It provides human-readable and JSON output.

## 5. Database Analysis

Location: `sql/`

The SQL layer supports transaction reporting, callback reconciliation, duplicate detection, processing-time analysis, and query optimization.

A composite index on `(transaction_ref, id DESC)` improves transaction-reference search performance.

## 6. Testing Architecture

| Component | Testing approach |
|---|---|
| API | Pytest and HTTPX |
| Database | PostgreSQL integration tests |
| CLI | Pytest unit tests |
| UI | Playwright browser tests |
| SQL performance | EXPLAIN ANALYZE |
| Kubernetes | YAML lint validation |
| Linux | GitHub Actions system investigation |

## 7. CI/CD Architecture

Location: `.github/workflows/ci.yml`

GitHub Actions executes independent validation jobs for:

1. Database and API integration.
2. Browser UI tests.
3. CLI unit tests.
4. SQL performance benchmarking.
5. Kubernetes manifest validation.
6. Linux system investigation and API health verification.

Test artifacts are uploaded by the relevant workflow jobs.

## 8. Kubernetes Architecture

Location: `kubernetes/`

The deployment configuration includes:

- MiniPay API Deployment with two replicas.
- API Service.
- PostgreSQL Deployment.
- PostgreSQL Service.
- Persistent Volume Claim.
- ConfigMap and Secrets.
- Readiness and liveness probes.
- Resource requests and limits.

The manifests are statically validated. A live Kubernetes or Rancher deployment has not been performed.

## 9. Configuration and Security

Application configuration is provided through environment variables.

Important settings:

- `DATABASE_URL`
- `MINIPAY_API_KEY`

Kubernetes credentials are represented by placeholder Secret values. Production credentials must be supplied securely during deployment.

## 10. Known Limitations

- Payment processing is a sample implementation and does not integrate with a real payment operator.
- Duplicate transaction-reference validation is application-level and is not protected against concurrent requests by a database unique constraint.
- Callback records are represented in the database, but a complete external callback delivery and retry worker is outside the current implementation.
- Kubernetes manifests require environment-specific image and secret configuration.
- Live Kubernetes/Rancher deployment has not been verified.
