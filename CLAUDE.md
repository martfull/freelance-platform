# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Secure freelance marketplace backend — a FastAPI modular monolith with PostgreSQL, end-to-end encryption (AES-GCM + RSA-OAEP/PSS), escrow payments, and audit logging. Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic 2.7, Docker Compose.

## Common Commands

All commands run via `make` and execute inside Docker containers:

```bash
make build          # Build and start containers
make up             # Start containers in background
make down           # Stop containers
make logs           # Stream API logs

make migrate        # Apply all Alembic migrations
make migration msg='describe change'  # Generate new migration
make downgrade      # Rollback last migration
make db-reset       # Drop volumes and re-migrate (dev only)

make test           # Run pytest with coverage
make test-v         # Verbose pytest output
make lint           # Run flake8 (max line length: 120)
make bandit         # Run Bandit SAST → security/reports/
```

To run a single test:
```bash
docker compose exec api pytest tests/test_health.py -v
```

API: http://localhost:8000 | Swagger: http://localhost:8000/docs

## Architecture

**Modular monolith** — one codebase, one DB, one deployment unit. Module boundaries are designed so services can be extracted later.

### Module Structure

Each of the 8 business modules under `backend/app/modules/` follows this pattern:

```
modules/<domain>/
├── models.py       # SQLAlchemy ORM models
├── schemas.py      # Pydantic request/response schemas
├── router.py       # FastAPI endpoints
├── service.py      # Business logic
├── repository.py   # Database queries
└── permissions.py  # Access control (RBAC) per endpoint
```

**Domains:** `accounts`, `marketplace`, `contracts`, `communication`, `delivery`, `payments`, `moderation`, `audit`

The `security` module (`backend/app/modules/security/`) is a technical utility module — not a business domain — containing:
- `aes_gcm.py` — AES-GCM encryption/decryption
- `rsa_oaep.py` — RSA-OAEP key wrapping for AES data keys
- `rsa_pss.py` — RSA-PSS digital signatures
- `hashing.py` — SHA-256 fingerprints
- `key_management.py` — Dual RSA key pair generation and rotation

### Cross-Cutting Infrastructure

```
backend/app/
├── core/           # Config, exceptions, logging, CORS/auth middleware
├── database/       # SQLAlchemy session, declarative base, transaction helpers
└── common/         # Shared enums, pagination, response templates, validators
```

### Key Architectural Patterns

- **RBAC:** Two-layer — system roles (`user/moderator/admin`) + contextual roles (`client/freelancer` per contract)
- **Dual RSA key pairs per user:** One pair for encryption (RSA-OAEP), one for signing (RSA-PSS)
- **AES-GCM for data:** All messages and file chunks encrypted at rest with per-resource AES keys, which are themselves RSA-OAEP wrapped per recipient
- **Contract state machine:** Lifecycle transitions in `contracts/state_machine.py`
- **Signed audit log:** Critical events (escrow, contract creation, dispute decisions) signed with RSA-PSS and recorded in `audit` module
- **Chunked file delivery:** Encrypted chunks stored in `storage/chunks/`, referenced in `delivery` module

## Environment Setup

Copy and edit the environment file before first run:
```bash
cp .env.example .env
```

Required vars: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`, `SECRET_KEY` (change in production), `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `STORAGE_PATH`.

## CI/CD

GitHub Actions pipelines (`.github/workflows/`):
- **ci.yml:** lint → test (with live PostgreSQL) → SAST → deploy-staging (on `develop` push)
- **sast.yml:** Bandit security scanning on push/PR and weekly schedule; fails on HIGH severity + HIGH confidence

SAST reports saved to `security/reports/`.

## Documentation

Comprehensive architecture docs in `docs/`: `ARCHITECTURE.md`, `SECURITY_ARCHITECTURE.md`, `DATABASE_DESIGN.md`, `API_SPEC.md`, `THREAT_MODEL.md`, `DEVELOPMENT_PLAN.md`, `rbac-matrix.md`.
