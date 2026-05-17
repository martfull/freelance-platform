# Architecture

## Architecture Style

Проєкт використовує **modular monolith**. Це один FastAPI backend-застосунок, який має одну кодову базу, одну основну базу даних і один deployment unit, але всередині розділений на незалежні модулі за відповідальністю.

Такий підхід підходить для стартової стадії проєкту, тому що він:

- простіший за microservices;
- добре підходить для FastAPI;
- дозволяє швидко реалізувати MVP;
- зберігає чіткі межі між доменами;
- не ускладнює транзакції між payments, contracts і moderation;
- дозволяє в майбутньому винести окремі модулі в сервіси.

## Final Project Structure

```text
app/
  main.py

  core/
    config.py
    exceptions.py
    logging.py
    middleware.py

  database/
    base.py
    session.py
    transactions.py

  common/
    enums.py
    pagination.py
    responses.py
    validators.py
    types.py

  modules/
    accounts/
    marketplace/
    contracts/
    communication/
    delivery/
    payments/
    moderation/
    security/
    audit/

alembic/
tests/
```

## Why Modules Are Inside `modules/`

`modules/` містить основні домени продукту — тобто те, що безпосередньо описує бізнес-логіку платформи.

```text
modules = що робить система
core/database/common = на чому система працює
```

Приклади:

- `accounts` відповідає за користувачів і доступ.
- `marketplace` відповідає за задачі та пропозиції.
- `contracts` відповідає за активну домовленість між сторонами.
- `payments` відповідає за simulated escrow.
- `security` відповідає за криптографічні операції.

Технічні частини, які не є бізнес-доменами, винесені окремо:

- `core` — конфігурація, middleware, exceptions, logging.
- `database` — підключення до PostgreSQL, SQLAlchemy session, transaction helpers.
- `common` — спільні enum-и, responses, pagination, validators.

## Top-Level Technical Modules

### main.py

Точка входу FastAPI-застосунку.

Відповідає за:

- створення `FastAPI()` app;
- підключення routers з доменних модулів;
- підключення middleware;
- health check endpoint;
- стартову конфігурацію API.

### core

Глобальні технічні налаштування застосунку.

```text
core/
  config.py
  exceptions.py
  logging.py
  middleware.py
```

- `config.py` — environment variables, database URL, JWT settings, storage path, crypto settings.
- `exceptions.py` — глобальні exception classes і error handlers.
- `logging.py` — налаштування логування.
- `middleware.py` — CORS, request ID, security headers, request logging.

`core` не містить бізнес-логіку.

### database

Основний технічний модуль роботи з базою даних.

```text
database/
  base.py
  session.py
  transactions.py
```

- `base.py` — SQLAlchemy `Base`, metadata, імпорт моделей для Alembic.
- `session.py` — database engine, session factory, `get_db` dependency.
- `transactions.py` — helper-и для atomic operations.

SQLAlchemy models не складаються всі в `database/`. Вони лежать у доменних модулях, наприклад `modules/accounts/models.py`, `modules/contracts/models.py`, `modules/payments/models.py`. Це зберігає ownership моделей біля їхньої бізнес-логіки.

### common

Спільні речі, які використовуються в багатьох модулях.

```text
common/
  enums.py
  pagination.py
  responses.py
  validators.py
  types.py
```

- `enums.py` — спільні enum-и: currency, generic statuses, system roles.
- `pagination.py` — pagination schemas і helpers.
- `responses.py` — стандартна структура API-відповідей і помилок.
- `validators.py` — reusable validators.
- `types.py` — спільні типи, наприклад UUID aliases.

## Business and Security Modules

### accounts

Акаунти, профілі, авторизація та ключі користувача.

```text
modules/accounts/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  dependencies.py
  jwt.py
  password.py
  permissions.py
```

Відповідає за:

- реєстрацію;
- login/logout;
- JWT access/refresh tokens;
- password hashing;
- профіль користувача;
- `system_role`: `user`, `moderator`, `admin`;
- public profile;
- records для двох RSA key pairs користувача;
- доступ до поточного користувача через dependencies.

### marketplace

Публікація задач і пропозиції виконавців.

```text
modules/marketplace/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  permissions.py
```

Відповідає за:

- створення task;
- редагування task;
- зміну ціни до створення contract;
- перегляд open tasks;
- пошук задач;
- створення offer;
- accept/reject offers;
- заборону відгуку на власну task.

### contracts

Активна домовленість між client і freelancer.

```text
modules/contracts/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  state_machine.py
  permissions.py
```

Відповідає за:

- створення contract після прийняття offer;
- підтвердження співпраці обома сторонами;
- статуси contract;
- перевірку, хто є `client`, а хто `freelancer`;
- перехід `pending_confirmation -> active -> submitted -> completed/disputed`;
- правила завершення роботи.

### communication

Захищена комунікація між сторонами contract.

```text
modules/communication/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  permissions.py
```

Відповідає за:

- encrypted chat messages;
- REST-based message sending;
- message history;
- перевірку, що користувач є учасником contract;
- зберігання тільки encrypted payload;
- майбутню підтримку WebSocket або notifications.

Plaintext-повідомлення тут не зберігаються.

### delivery

Передача результатів роботи: файли, chunks і storage adapter.

```text
modules/delivery/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  chunking.py
  storage_interface.py
  local_storage.py
  s3_storage.py
  permissions.py
```

Відповідає за:

- ініціалізацію upload;
- encrypted chunk upload;
- chunk metadata;
- local file storage для MVP;
- S3-compatible storage у майбутньому;
- перевірку SHA-256 фінального файлу;
- доступ до файлів тільки для учасників contract.

Фізично файл зберігається не в PostgreSQL, а як encrypted chunks у local storage або S3.

### payments

Simulated escrow, balance і фінансовий ledger.

```text
modules/payments/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  ledger.py
  permissions.py
```

Відповідає за:

- simulated user balance;
- deposit;
- escrow hold;
- release коштів freelancer-у;
- refund client-у;
- transaction ledger;
- перевірку достатності балансу;
- фінансові status transitions.

`ledger.py` потрібен, щоб фінансові операції були записані як події, а не просто зміна числа в балансі.

### moderation

Спори й модерація.

```text
modules/moderation/
  router.py
  models.py
  schemas.py
  service.py
  repository.py
  permissions.py
```

Відповідає за:

- створення dispute;
- перегляд dispute;
- додавання reason/evidence metadata;
- призначення moderator;
- рішення moderator-а;
- запуск release/refund через `payments`;
- обмеження доступу тільки для учасників contract і moderator/admin.

### security

Криптографічний технічний модуль, який використовується бізнес-модулями.

```text
modules/security/
  aes_gcm.py
  rsa_oaep.py
  rsa_pss.py
  hashing.py
  key_management.py
  crypto_schemas.py
```

Відповідає за:

- `aes_gcm.py` — AES-GCM encryption/decryption повідомлень і chunks.
- `rsa_oaep.py` — шифрування AES-ключів через RSA-OAEP.
- `rsa_pss.py` — цифровий підпис і перевірка підпису через RSA-PSS.
- `hashing.py` — SHA-256 для файлів і payload fingerprints.
- `key_management.py` — генерація двох RSA key pairs, key rotation, key metadata.
- `crypto_schemas.py` — структури encrypted payload, encrypted key, signature metadata.

`security` не вирішує бізнес-правила. Він не знає, хто client чи freelancer. Він надає тільки crypto operations.

### audit

Журнал критичних подій.

```text
modules/audit/
  models.py
  schemas.py
  service.py
  repository.py
  event_builder.py
```

Відповідає за:

- запис security-relevant events;
- escrow operation logs;
- contract confirmation logs;
- failed integrity verification logs;
- dispute decision logs;
- payload hash;
- signature metadata.

Приклади подій:

```text
TASK_PRICE_CHANGED
OFFER_ACCEPTED
CONTRACT_CONFIRMED
ESCROW_HELD
ESCROW_RELEASED
FILE_VERIFICATION_FAILED
DISPUTE_RESOLVED
```

## Module Dependency Rule

Базове правило залежностей:

```text
router -> service -> repository -> database
```

- `router.py` приймає HTTP-запит і викликає service.
- `service.py` містить бізнес-логіку.
- `repository.py` працює з SQLAlchemy queries.
- `models.py` описує таблиці домену.
- `schemas.py` описує Pydantic request/response models.
- `permissions.py` містить ownership та role checks.

Модулі не повинні напряму змінювати таблиці інших модулів. Якщо `moderation` має зробити refund, він викликає `payments.service.refund(...)`, а не напряму змінює balances.

## High-Level Data Flow

### Contract Creation

```text
User creates task
        |
Other user creates offer
        |
Client accepts offer
        |
Freelancer confirms
        |
System creates contract
        |
Client deposits funds into escrow
        |
Contract becomes active
```

### Encrypted Message

```text
Sender writes message
        |
Backend validates contract membership
        |
Message is encrypted with AES-GCM
        |
AES key is wrapped with RSA-OAEP
        |
Encrypted payload is stored
        |
Receiver requests messages
        |
Backend returns encrypted payload and metadata
```

### Encrypted File Upload

```text
Client initializes file upload
        |
System creates file_id and metadata
        |
File is split into 1 MB chunks
        |
Each chunk is encrypted with AES-GCM using unique nonce
        |
Chunks are stored in local/S3-compatible storage
        |
Metadata is stored in PostgreSQL
        |
Final SHA-256 is verified after upload completion
```

## Deployment Model

MVP може запускатися як один backend service:

```text
FastAPI app + PostgreSQL + local file storage
```

Production-ready модель:

```text
FastAPI app + PostgreSQL + Redis + S3/MinIO + reverse proxy + monitoring
```
