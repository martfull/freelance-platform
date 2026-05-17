# Development Plan

## Phase 1: Project Foundation

Ціль: підготувати базову структуру backend-застосунку.

Tasks:

- Створити FastAPI project structure.
- Додати `core/`, `database/`, `common/` і `modules/`.
- Налаштувати PostgreSQL connection.
- Додати SQLAlchemy models і Alembic migrations.
- Налаштувати Pydantic schemas.
- Додати базову error response model.
- Додати environment configuration.

## Phase 2: Accounts

Ціль: реалізувати identity layer.

Tasks:

- Реєстрація користувача.
- Login flow.
- Password hashing через Argon2 або bcrypt.
- JWT access/refresh tokens.
- `GET /users/me`.
- RBAC для `user`, `moderator`, `admin`.
- Records для `rsa_encryption` і `rsa_signing` public keys.

Acceptance criteria:

- Користувач може зареєструватися і залогінитися.
- Protected endpoints не доступні без JWT.
- Password не зберігається у plaintext.
- Для користувача можна зберегти окремі public keys для encryption і signing.

## Phase 3: Marketplace and Contracts

Ціль: реалізувати основний marketplace flow.

Tasks:

- CRUD для tasks у `marketplace`.
- Перегляд open tasks.
- Створення offers.
- Заборона offer на власну task.
- Accept offer flow.
- Contract confirmation by both parties у `contracts`.

Acceptance criteria:

- User може створювати tasks і приймати чужі tasks.
- Task price можна змінити до contract creation.
- Contract не стає active без підтвердження сторін.

## Phase 4: Payments MVP

Ціль: реалізувати simulated escrow у `payments`.

Tasks:

- Створити escrow account для user.
- Deposit simulated funds.
- Hold amount for contract.
- Release funds to freelancer.
- Refund funds to client.
- Audit escrow operations.
- Вести transaction ledger.

Acceptance criteria:

- Funds переходять з available balance у held balance.
- Release змінює balances коректно.
- Refund повертає funds client-у.
- Критичні операції записуються в audit log.

## Phase 5: Security Module

Ціль: реалізувати криптографічний модуль.

Tasks:

- `aes_gcm.py` для encrypt/decrypt.
- `rsa_oaep.py` для AES key wrapping.
- `rsa_pss.py` для signing/verification.
- `hashing.py` для SHA-256.
- `key_management.py` для двох RSA key pairs і key metadata.
- Tests for tampered payloads.

Acceptance criteria:

- Змінений ciphertext не проходить verification.
- AES key може бути wrapped/unwrapped через RSA-OAEP.
- Signature verification працює через RSA-PSS для critical payloads.

## Phase 6: Communication

Ціль: реалізувати encrypted REST communication.

Tasks:

- `POST /contracts/{contract_id}/messages`.
- `GET /contracts/{contract_id}/messages`.
- Access only for contract participants.
- Store only encrypted message payload.

Acceptance criteria:

- Plaintext message не зберігається в БД.
- Сторонній user не може прочитати communication history.
- Tampered message відхиляється.

## Phase 7: Delivery

Ціль: реалізувати encrypted chunk-based file transfer.

Tasks:

- File upload initialization.
- Chunk upload endpoint.
- Local storage adapter.
- S3-compatible adapter interface for future use.
- Final SHA-256 verification.
- File metadata and chunks metadata.

Acceptance criteria:

- Large file може передаватися chunks по 1 MB.
- Кожен chunk має унікальний nonce.
- Змінений chunk не проходить verification.
- Final file hash збігається після upload completion.

## Phase 8: Moderation

Ціль: реалізувати базовий dispute flow.

Tasks:

- User can open dispute for own contract.
- Moderator can review dispute.
- Moderator can resolve with release/refund.
- Decision is recorded in audit log.

Acceptance criteria:

- User не може вирішувати dispute.
- Moderator decision змінює payments state.
- Усі рішення логуються.

## Phase 9: Security Testing and Documentation Update

Ціль: підготувати проєкт до демонстрації.

Tasks:

- Pytest coverage for core flows.
- Bandit scan.
- API documentation review.
- Threat model update.
- Demo scenarios.

Demo scenarios:

- Create task -> create offer -> confirm contract.
- Deposit -> hold -> submit work -> release.
- Encrypted message success.
- Tampered message rejection.
- Encrypted chunk upload and hash verification.
- Dispute resolution by moderator.
