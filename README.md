# Secure Freelance Marketplace

Платформа для безпечної організації freelance-роботи між користувачами.

**Стек:** FastAPI · PostgreSQL · SQLAlchemy · Alembic · AES-GCM · RSA-OAEP · RSA-PSS · SHA-256 · Docker · Nginx

## Quick Start

```bash
cp .env.example .env
make build
```

API: http://localhost/docs

## Make команди

```bash
make build          # зібрати і запустити всі контейнери
make up             # запустити без rebuild
make down           # зупинити
make logs           # логи api
make nginx-logs     # логи nginx

make migrate        # застосувати міграції
make migration msg='...'  # згенерувати нову міграцію
make downgrade      # відкотити останню міграцію
make db-reset       # дропнути і перемігрувати (тільки dev)

make test           # pytest з coverage
make test-v         # pytest verbose
make lint           # flake8
make bandit         # Bandit SAST → security/reports/
```

## Архітектура

```
backend/app/
  core/               — config, exceptions, logging, middleware
  database/           — SQLAlchemy base, session, transactions
  common/             — enums, pagination, responses, validators

  modules/
    accounts/         — реєстрація, JWT, RBAC, RSA key records
    marketplace/      — tasks, offers
    contracts/        — lifecycle, state machine
    communication/    — encrypted REST chat
    delivery/         — encrypted chunk-based file upload
    payments/         — simulated escrow, ledger
    moderation/       — disputes, рішення модератора
    security/         — AES-GCM, RSA-OAEP, RSA-PSS, SHA-256
    audit/            — audit log, підписані критичні події

nginx/                — reverse proxy, rate limiting
alembic/              — міграції бази даних
docs/                 — архітектурна документація
security/reports/     — SAST звіти (генеруються CI)
storage/              — encrypted file chunks (не комітяться)
```

## Infrastructure

| Сервіс | Образ | Роль |
|---|---|---|
| `api` | python:3.12-slim (multi-stage) | FastAPI застосунок |
| `db` | postgres:16-alpine | База даних |
| `nginx` | nginx:1.27-alpine | Reverse proxy, rate limiting |

**Multi-stage Dockerfile:** `dev` (з pytest/flake8/bandit) і `production` (тільки runtime).  
`docker-compose.override.yml` автоматично застосовується локально для dev режиму.

## CI/CD Pipeline

```
lint ──┐
sca  ──┼──→ test → sast ──┐
trivy ─┘                  ├──→ deploy → сервер 83.10.125.96
                 trivy ───┘
```

| Job | Що робить |
|---|---|
| `lint` | flake8, max-line-length 120 |
| `sca` | pip-audit — CVE у Python залежностях |
| `trivy` | сканування образу і Dockerfile на вразливості |
| `test` | pytest + live PostgreSQL |
| `sast` | Bandit — падає на HIGH severity + HIGH confidence |
| `deploy` | SSH → git pull → docker compose up → alembic upgrade |

**Деплой** відбувається автоматично при push в `main` після проходження всіх перевірок.

## DevSecOps

| Інструмент | Рівень | Що ловить |
|---|---|---|
| flake8 | code | стиль і синтаксис |
| pip-audit | SCA | CVE у залежностях |
| Bandit | SAST | вразливості у коді |
| Trivy | container | OS і Python вразливості в образі |
| SARIF | reporting | результати → GitHub Security tab |
| Dependabot | supply chain | автоматичні PR для оновлень |
| Nginx rate limiting | runtime | 30 req/s загальний, 5 req/s auth |

## Security

- AES-GCM для шифрування messages і file chunks
- RSA-OAEP для key wrapping
- RSA-PSS для підпису critical events
- SHA-256 для file fingerprint і payload hashes
- JWT access/refresh tokens · Argon2 password hashing
- RBAC: system roles (user/moderator/admin) + contextual roles (client/freelancer)
- Audit log для всіх критичних подій

## Документація

`docs/` містить повну архітектурну документацію:
[Architecture](docs/ARCHITECTURE.md) · [Security](docs/SECURITY_ARCHITECTURE.md) · [Database](docs/DATABASE_DESIGN.md) · [API Spec](docs/API_SPEC.md) · [Threat Model](docs/THREAT_MODEL.md) · [RBAC Matrix](docs/rbac-matrix.md)
