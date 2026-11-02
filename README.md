# MiniPay – Payment API Technical Assessment

## Overview

MiniPay is a sample payment processing system developed to demonstrate API engineering, database analysis, incident investigation, operational troubleshooting, and automated testing.

The project includes a FastAPI backend, PostgreSQL database, browser-based dashboard, Python transaction support CLI, SQL analysis, Kubernetes manifests, and GitHub Actions CI workflows.

## Technology Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **API Testing:** Pytest, HTTPX
- **UI Testing:** Playwright
- **Database Analysis:** PostgreSQL SQL and EXPLAIN ANALYZE
- **Container Orchestration:** Kubernetes YAML manifests
- **CI/CD:** GitHub Actions

## Repository Structure

| Path | Description |
|---|---|
| `application/api/` | FastAPI application, routes, models, and services |
| `application/ui/` | MiniPay browser dashboard |
| `investigation/` | Incident RCA and system investigation reports |
| `sql/` | Database schema, data generator, analysis, and performance tests |
| `kubernetes/` | API and database deployment manifests and operations guide |
| `python/` | Transaction support CLI |
| `tests/api/` | API and database integration tests |
| `tests/ui/` | Browser-based UI tests |
| `evidence/` | Linux investigation script and evidence |
| `.github/workflows/` | Automated CI workflows |

## Main Features

### Payment API

- Create customers.
- Submit payment transactions.
- Retrieve payment details.
- Search payments by transaction reference.
- Retrieve customer payment history.
- Check application and database health.
- Protect merchant API endpoints using API-key authentication.

### Python Support CLI

Retrieve transaction information and investigate anomalies:

```bash
python python/support_tool.py --transaction TXN000123
```

For machine-readable output:

```bash
python python/support_tool.py --transaction TXN000123 --json
```

The tool checks transaction details, customer information, callback attempts, and potential issues.

### SQL Analysis

The SQL scripts cover:

- Transaction totals by status and date.
- Top customers by successful payment value.
- Long-running PROCESSING transactions.
- Duplicate transaction references.
- Daily success rates.
- Callback reconciliation.
- Average and percentile processing times.
- Search-query performance optimization.

## Setup

See [SETUP.md](SETUP.md) for installation, database initialization, environment variables, and execution instructions.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the application components and their interactions.

## Incident Investigations

The `investigation/` directory contains findings and root cause analysis for:

1. Intermittent payment search HTTP 500 errors.
2. Kubernetes pods starting without making the API accessible.
3. Slow transaction searches as database volume increases.

These are assessment investigations. Simulated failures and static manifest reviews are identified as such rather than presented as reproduced production incidents.

## Automated Validation

GitHub Actions provides automated checks for:

- Database schema and API integration tests.
- Browser UI tests.
- Python CLI unit tests.
- SQL performance benchmarking.
- Kubernetes YAML validation.
- Linux system investigation and MiniPay health checks.

See the repository's **Actions** tab for individual workflow results and generated evidence artifacts.

## Kubernetes Deployment

Kubernetes manifests and operational commands are available under `kubernetes/`.

The manifests have been statically validated. A live Kubernetes or Rancher deployment has not been claimed as part of this assessment.

## Evidence and Documentation

- `sql/PERFORMANCE.md` – SQL benchmark findings.
- `investigation/` – Incident and system investigation reports.
- `evidence/` – Linux investigation script and CI-generated evidence.
- `AI_USAGE.md` – AI assistance and validation disclosure.

## Security Notes

- Do not commit production credentials, private keys, or real customer information.
- Configure API keys and database credentials through environment variables or Kubernetes Secrets.
- The included credentials are placeholders intended for local or CI testing.

## Project Status

This repository is an assessment implementation. CI validation results and documented limitations should be used to distinguish tested functionality from infrastructure that has only been prepared or statically validated.
