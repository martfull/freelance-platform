# Secure Freelance Marketplace

Платформа для безпечної організації freelance-роботи між користувачами.

**Стек:** FastAPI · PostgreSQL · SQLAlchemy · AES-GCM · RSA-OAEP · RSA-PSS · SHA-256

## Quick Start

```bash
cp .env.example .env
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

API docs: http://localhost:8000/docs

## Structure

```
backend/app/
  auth/        JWT, login, register, password hashing
  users/       profiles, public data
  tasks/       CRUD, search, statuses
  offers/      offer flow, accept/reject
  orders/      order lifecycle
  chat/        encrypted REST messaging
  files/       encrypted chunk-based upload
  escrow/      simulated escrow
  disputes/    dispute flow, moderator decision
  security/    AES-GCM, RSA-OAEP, RSA-PSS, SHA-256
  audit/       audit log
```

## CI/CD

| Job | Trigger | What it does |
|---|---|---|
| lint | push/PR → develop, main | flake8 |
| test | after lint | pytest + PostgreSQL service |
| sast | after test | Bandit, fails on HIGH severity |
| deploy-staging | push → develop | deploy stub |

## Security

- AES-GCM для шифрування messages і file chunks
- RSA-OAEP для key wrapping
- RSA-PSS для підпису critical events
- SHA-256 для file fingerprint
- JWT access/refresh tokens
- Argon2 password hashing
- Audit log для всіх критичних дій

## Team

| Role | Responsibility |
|---|---|
| IoT Architect / Team Lead | Threat model, CIA matrix, risk matrix |
| Firmware & Encryption | Crypto module (security/) |
| Network Security | RBAC, SAST, CI/CD, audit monitoring, frontend |
