# MiniPay Setup Guide

## 1. Prerequisites

Install the following:

- Python 3.11 or later
- PostgreSQL 16
- Git
- A terminal (PowerShell, Command Prompt, or Linux shell)

## 2. Clone the Repository

```bash
git clone https://github.com/syedrohan/minipay-technical-assignment.git
cd minipay-technical-assignment
```

## 3. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure PostgreSQL

Create a database named `minipay`.

For example, using PostgreSQL:

```sql
CREATE DATABASE minipay;
```

Apply the database schema from the repository root:

```bash
psql -U postgres -d minipay -f sql/schema.sql
```

Ensure PostgreSQL is running and the database credentials are correct.

## 6. Configure Environment Variables

The application requires a database connection URL and API key.

**Linux/macOS:**

```bash
export DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/minipay"
export MINIPAY_API_KEY="your-local-test-api-key"
```

**Windows PowerShell:**

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/minipay"
$env:MINIPAY_API_KEY="your-local-test-api-key"
```

Replace `YOUR_PASSWORD` with your local PostgreSQL password. Do not commit real credentials to GitHub.

## 7. Start the MiniPay API

From the repository root:

```bash
uvicorn application.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Application URLs:

- Dashboard: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

The health endpoint checks application database connectivity.

## 8. Run Automated Tests

Run API and database integration tests:

```bash
python -m pytest tests/api -v
```

Run CLI unit tests:

```bash
python -m pytest tests/test_support_tool.py -v
```

Run browser UI tests:

```bash
python -m playwright install chromium
python -m pytest tests/ui -v
```

Run all tests:

```bash
python -m pytest -v
```

## 9. Use the Python Support Tool

Look up a transaction using its reference:

```bash
python python/support_tool.py --transaction TXN000123
```

Get JSON output:

```bash
python python/support_tool.py --transaction TXN000123 --json
```

The CLI uses the same `DATABASE_URL` environment variable as the API.

## 10. API Authentication

Merchant API endpoints require the `X-API-Key` header.

Example:

```bash
curl -H "X-API-Key: your-local-test-api-key" \
  http://127.0.0.1:8000/api/payments/search/TXN000123
```

The `/health` endpoint is public and does not require this header.

## 11. SQL Analysis

SQL scripts are available under `sql/`.

- `schema.sql` – database schema.
- `generate_data.py` – deterministic sample data generator.
- `analysis_queries.sql` – transaction analysis and reconciliation.
- `performance_test.sql` – query execution plan and index benchmark.
- `PERFORMANCE.md` – recorded benchmark findings.

Run the SQL scripts against the `minipay` database using `psql`.

## 12. Kubernetes

See `kubernetes/OPERATIONS.md` for manifest validation, deployment commands, health checks, logs, and troubleshooting.

A working Kubernetes cluster is required for actual deployment. The repository's manifests have been statically validated; live deployment is not claimed.
