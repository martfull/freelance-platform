# Database Design

## Overview

PostgreSQL використовується як основне сховище структурованих даних. Файли не зберігаються напряму в базі даних. У PostgreSQL зберігається metadata, а encrypted file chunks зберігаються в local або S3-compatible object storage через модуль `delivery`.

## Database Module

Технічний модуль роботи з БД знаходиться на верхньому рівні `app/database/`.

```text
database/
  base.py
  session.py
  transactions.py
```

- `base.py` — SQLAlchemy `Base`, metadata, імпорт моделей для Alembic.
- `session.py` — engine, session factory, `get_db` dependency.
- `transactions.py` — helper-и для atomic operations.

SQLAlchemy models зберігаються в доменних модулях, бо кожна таблиця належить конкретному домену.

## Main Entities

```text
users
user_keys
tasks
offers
contracts
messages
file_assets
file_chunks
escrow_accounts
escrow_transactions
disputes
audit_logs
```

## users

Модуль: `modules/accounts`.

```text
id UUID PK
email VARCHAR UNIQUE NOT NULL
password_hash VARCHAR NOT NULL
display_name VARCHAR NOT NULL
system_role VARCHAR NOT NULL DEFAULT 'user'
status VARCHAR NOT NULL DEFAULT 'active'
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

`system_role`: `user`, `moderator`, `admin`.

Звичайний користувач може бути і client, і freelancer залежно від контексту task/contract.

## user_keys

Модуль: `modules/accounts`.

```text
id UUID PK
user_id UUID FK users.id
key_type VARCHAR NOT NULL
public_key_pem TEXT NOT NULL
private_key_reference TEXT NULL
status VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
rotated_at TIMESTAMP NULL
```

Private keys не повинні зберігатися у відкритому вигляді. Encryption private key і signing private key мають різне призначення та керуються окремо.

Допустимі значення `key_type`:

```text
rsa_encryption
rsa_signing
```

`rsa_encryption` використовується тільки для RSA-OAEP key wrapping. `rsa_signing` використовується тільки для RSA-PSS digital signatures.

## tasks

Модуль: `modules/marketplace`.

```text
id UUID PK
creator_id UUID FK users.id
title VARCHAR NOT NULL
description TEXT NOT NULL
budget_amount NUMERIC NOT NULL
currency VARCHAR NOT NULL DEFAULT 'USD'
status VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Статуси: `draft`, `open`, `in_negotiation`, `contracted`, `cancelled`, `closed`.

Ціну можна змінювати до переходу task у `contracted`.

## offers

Модуль: `modules/marketplace`.

```text
id UUID PK
task_id UUID FK tasks.id
freelancer_id UUID FK users.id
message TEXT NULL
proposed_amount NUMERIC NULL
status VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Статуси: `pending`, `accepted`, `rejected`, `withdrawn`.

Користувач не може створити offer на власну task.

## contracts

Модуль: `modules/contracts`.

Contract створюється після accept offer і підтвердження сторін.

```text
id UUID PK
task_id UUID FK tasks.id
client_id UUID FK users.id
freelancer_id UUID FK users.id
amount NUMERIC NOT NULL
currency VARCHAR NOT NULL
status VARCHAR NOT NULL
client_confirmed_at TIMESTAMP NULL
freelancer_confirmed_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

Статуси: `pending_confirmation`, `active`, `submitted`, `completed`, `disputed`, `cancelled`.

## messages

Модуль: `modules/communication`.

Зберігає encrypted communication messages.

```text
id UUID PK
contract_id UUID FK contracts.id
sender_id UUID FK users.id
recipient_id UUID FK users.id
algorithm VARCHAR NOT NULL
nonce TEXT NOT NULL
ciphertext TEXT NOT NULL
tag TEXT NOT NULL
encrypted_key TEXT NOT NULL
created_at TIMESTAMP NOT NULL
```

Plaintext повідомлення не зберігається в БД.

## file_assets

Модуль: `modules/delivery`.

Metadata файлів, які передаються в contract.

```text
id UUID PK
contract_id UUID FK contracts.id
uploader_id UUID FK users.id
original_filename VARCHAR NOT NULL
content_type VARCHAR NULL
file_size BIGINT NOT NULL
chunk_size INTEGER NOT NULL
chunks_count INTEGER NOT NULL
sha256_hash VARCHAR NOT NULL
algorithm VARCHAR NOT NULL
encrypted_key TEXT NOT NULL
status VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
completed_at TIMESTAMP NULL
```

Статуси: `initialized`, `uploading`, `completed`, `failed`, `rejected`.

## file_chunks

Модуль: `modules/delivery`.

Metadata encrypted chunks.

```text
id UUID PK
file_id UUID FK file_assets.id
chunk_index INTEGER NOT NULL
storage_path TEXT NOT NULL
nonce TEXT NOT NULL
tag TEXT NOT NULL
chunk_size INTEGER NOT NULL
created_at TIMESTAMP NOT NULL
```

Constraint: `unique(file_id, chunk_index)`.

## escrow_accounts

Модуль: `modules/payments`.

Simulated balance користувачів.

```text
id UUID PK
user_id UUID FK users.id
available_balance NUMERIC NOT NULL
held_balance NUMERIC NOT NULL
currency VARCHAR NOT NULL
updated_at TIMESTAMP NOT NULL
```

## escrow_transactions

Модуль: `modules/payments`.

Фіксує всі операції з simulated escrow.

```text
id UUID PK
contract_id UUID FK contracts.id NULL
payer_id UUID FK users.id NULL
receiver_id UUID FK users.id NULL
amount NUMERIC NOT NULL
currency VARCHAR NOT NULL
type VARCHAR NOT NULL
status VARCHAR NOT NULL
payload_hash VARCHAR NOT NULL
signature TEXT NULL
created_at TIMESTAMP NOT NULL
```

Типи: `deposit`, `hold`, `release`, `refund`, `adjustment`.

## disputes

Модуль: `modules/moderation`.

Спірні ситуації по contracts.

```text
id UUID PK
contract_id UUID FK contracts.id
opened_by_id UUID FK users.id
moderator_id UUID FK users.id NULL
reason TEXT NOT NULL
status VARCHAR NOT NULL
resolution TEXT NULL
created_at TIMESTAMP NOT NULL
resolved_at TIMESTAMP NULL
```

Статуси: `open`, `under_review`, `resolved`, `rejected`.

## audit_logs

Модуль: `modules/audit`.

Журнал критичних подій.

```text
id UUID PK
actor_id UUID FK users.id NULL
entity_type VARCHAR NOT NULL
entity_id UUID NOT NULL
action VARCHAR NOT NULL
payload_hash VARCHAR NOT NULL
signature TEXT NULL
ip_address VARCHAR NULL
created_at TIMESTAMP NOT NULL
```

## Important Indexes

```text
users.email
tasks.status
tasks.creator_id
offers.task_id
offers.freelancer_id
contracts.client_id
contracts.freelancer_id
messages.contract_id
file_assets.contract_id
file_chunks.file_id + chunk_index
escrow_transactions.contract_id
disputes.status
audit_logs.entity_type + entity_id
```

## Data Protection Rules

- Passwords не зберігаються у plaintext.
- Messages зберігаються тільки encrypted.
- File contents зберігаються тільки encrypted у local/S3-compatible storage.
- Escrow critical records мають payload hash.
- Audit logs не повинні містити plaintext secrets або private keys.
