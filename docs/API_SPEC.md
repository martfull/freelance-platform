# API Spec

## Overview

API проєкту будується на FastAPI і має REST-first підхід. OpenAPI/Swagger використовується для тестування, демонстрації та документації endpoint-ів.

Усі protected endpoints використовують JWT access token:

```http
Authorization: Bearer <access_token>
```

API згрупований відповідно до фінальних доменних модулів: `accounts`, `marketplace`, `contracts`, `communication`, `delivery`, `payments`, `moderation`.

## Accounts API

### POST /auth/register

Створює нового користувача.

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "display_name": "Alex"
}
```

### POST /auth/login

Повертає access і refresh tokens.

```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

### POST /auth/refresh

Оновлює access token за refresh token.

### GET /users/me

Повертає профіль поточного користувача.

### GET /users/{user_id}

Повертає public profile користувача.

## Marketplace API

### POST /tasks

Створює task.

```json
{
  "title": "Build landing page",
  "description": "Need a responsive landing page for SaaS product.",
  "budget_amount": 300,
  "currency": "USD"
}
```

### GET /tasks

Повертає список відкритих tasks.

Query parameters: `status`, `search`, `min_budget`, `max_budget`, `page`, `limit`.

### GET /tasks/{task_id}

Повертає деталі task.

### PATCH /tasks/{task_id}

Оновлює task. Доступно тільки creator-у task до створення contract.

### POST /tasks/{task_id}/offers

Створює offer на task.

Rules:

- користувач не може створити offer на власну task;
- task має бути у статусі `open` або `in_negotiation`.

### GET /tasks/{task_id}/offers

Повертає offers для task. Доступно creator-у task.

### POST /offers/{offer_id}/accept

Client приймає offer і запускає contract creation flow.

## Contracts API

### POST /contracts/{contract_id}/confirm

Підтверджує участь сторони в contract.

Rules:

- client і freelancer мають підтвердити contract;
- після двох підтверджень contract може перейти в `active` після escrow hold.

### GET /contracts/{contract_id}

Повертає contract details. Доступно тільки учасникам contract або moderator/admin.

### POST /contracts/{contract_id}/submit

Freelancer позначає роботу як submitted.

### POST /contracts/{contract_id}/complete

Client підтверджує завершення роботи і запускає escrow release.

## Communication API

### POST /contracts/{contract_id}/messages

Створює encrypted message.

```json
{
  "recipient_id": "uuid",
  "algorithm": "AES-GCM",
  "nonce": "base64",
  "ciphertext": "base64",
  "tag": "base64",
  "encrypted_key": "base64"
}
```

### GET /contracts/{contract_id}/messages

Повертає encrypted message history для учасників contract.

## Delivery API

### POST /contracts/{contract_id}/files/init

Ініціалізує encrypted file upload.

```json
{
  "original_filename": "result.zip",
  "content_type": "application/zip",
  "file_size": 5242880,
  "chunk_size": 1048576,
  "sha256_hash": "hex",
  "algorithm": "AES-GCM",
  "encrypted_key": "base64"
}
```

### POST /files/{file_id}/chunks

Завантажує encrypted chunk.

```json
{
  "chunk_index": 0,
  "nonce": "base64",
  "tag": "base64",
  "ciphertext": "base64"
}
```

### POST /files/{file_id}/complete

Завершує upload і запускає verification.

### GET /files/{file_id}

Повертає file metadata і download information для authorized user.

## Payments API

### POST /payments/deposit

Поповнює simulated balance.

```json
{
  "amount": 500,
  "currency": "USD"
}
```

### POST /contracts/{contract_id}/escrow/hold

Блокує кошти client-а під contract.

### POST /contracts/{contract_id}/escrow/release

Переказує held funds freelancer-у після завершення роботи.

### POST /contracts/{contract_id}/escrow/refund

Повертає held funds client-у. Зазвичай викликається після moderator decision.

## Moderation API

### POST /contracts/{contract_id}/disputes

Створює dispute.

```json
{
  "reason": "Client does not confirm completed work."
}
```

### GET /disputes/{dispute_id}

Повертає dispute details.

### POST /disputes/{dispute_id}/resolve

Moderator вирішує dispute.

```json
{
  "decision": "release",
  "resolution": "Work was delivered and verified. Funds released to freelancer."
}
```

Можливі `decision`: `release`, `refund`, `partial_refund`, `reject`.

## Error Model

Detailed error handling rules are documented in [ERROR_HANDLING.md](ERROR_HANDLING.md).

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have access to this resource.",
    "details": {}
  }
}
```

## Important Status Codes

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```
