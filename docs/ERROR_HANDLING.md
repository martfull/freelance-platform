# Error Handling

## Overview

Проєкт використовує єдиний формат помилок для всіх API endpoints. Це потрібно, щоб backend, frontend і тести однаково розуміли помилки незалежно від модуля: `accounts`, `marketplace`, `contracts`, `payments`, `delivery`, `moderation` або `security`.

Базова реалізація знаходиться в:

```text
backend/app/core/exceptions.py
backend/app/common/responses.py
```

## Standard Error Response

Усі application errors мають повертатися в такому форматі:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have access to this resource.",
    "details": {}
  }
}
```

Поля:

- `code` — стабільний машинний код помилки, який може використовувати frontend.
- `message` — людське пояснення помилки.
- `details` — додаткові структуровані дані, наприклад `task_id`, `contract_id`, `field`.

## Current Application Exceptions

| Exception | HTTP Status | Error Code | When To Use |
|---|---:|---|---|
| `AppError` | `400 Bad Request` | `APP_ERROR` | Загальна помилка застосунку, якщо немає точнішого типу. |
| `NotFoundError` | `404 Not Found` | `NOT_FOUND` | Ресурс не існує або користувач не має бачити, що він існує. |
| `PermissionDeniedError` | `403 Forbidden` | `FORBIDDEN` | Користувач авторизований, але не має доступу до ресурсу або дії. |
| `ConflictError` | `409 Conflict` | `CONFLICT` | Запит формально правильний, але конфліктує з поточним станом системи або бізнес-правилом. |

## HTTP Status Code Rules

### 400 Bad Request

Використовувати, коли запит некоректний або дія не може бути виконана через неправильні вхідні дані.

Приклади:

- invalid encrypted payload;
- invalid chunk metadata;
- unsupported algorithm;
- malformed public key.

У коді:

```python
raise AppError("Invalid encrypted payload")
```

### 401 Unauthorized

Використовувати, коли користувач не автентифікований або token невалідний.

Приклади:

- access token missing;
- access token expired;
- invalid JWT signature.

Планований exception:

```python
class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UNAUTHORIZED"
```

### 403 Forbidden

Використовувати, коли користувач відомий системі, але не має права виконати дію.

Приклади:

- user не є учасником contract;
- user намагається читати чужі messages;
- user намагається вирішити dispute без ролі `moderator`;
- freelancer намагається підтвердити completion замість client.

У коді:

```python
raise PermissionDeniedError("Only contract participants can access messages")
```

### 404 Not Found

Використовувати, коли ресурс не знайдено.

Приклади:

- task не існує;
- contract не існує;
- file metadata не існує;
- dispute не існує.

У коді:

```python
raise NotFoundError("Task not found")
```

### 409 Conflict

Використовувати для конфліктів бізнес-логіки.

Приклади:

- user створює offer на власну task;
- task уже перейшла в contract і ціну не можна змінити;
- escrow уже released;
- contract уже completed;
- user email already exists.

У коді:

```python
raise ConflictError("Cannot create offer for your own task")
```

### 422 Validation Error

Цей status зазвичай автоматично повертає FastAPI/Pydantic, коли request body або query parameters не проходять schema validation.

Приклади:

- поле `email` має неправильний формат;
- `amount` не є числом;
- required field відсутній;
- `limit` більше дозволеного максимуму.

Для Pydantic validation errors не потрібно вручну кидати `AppError`, якщо стандартної FastAPI-відповіді достатньо.

### 500 Internal Server Error

Використовувати тільки для неочікуваних помилок сервера.

Приклади:

- unexpected database failure;
- unhandled exception;
- storage adapter failure без контрольованої причини.

Не треба навмисно кидати `500` для бізнес-помилок. Якщо помилку можна пояснити користувачу, краще використовувати `400`, `403`, `404` або `409`.

## Security-Specific Future Error Codes

Для security module пізніше варто додати окремі codes:

| Error Code | Suggested HTTP Status | When To Use |
|---|---:|---|
| `INVALID_SIGNATURE` | `400` | RSA-PSS signature verification failed. |
| `INTEGRITY_CHECK_FAILED` | `400` | AES-GCM tag або SHA-256 verification failed. |
| `INVALID_PUBLIC_KEY` | `400` | Public key має неправильний формат або не підтримується. |
| `KEY_NOT_FOUND` | `404` | Потрібний public key не знайдено. |
| `UNSUPPORTED_ALGORITHM` | `400` | Payload вказує алгоритм, який система не підтримує. |

## Payments-Specific Future Error Codes

Для payments module пізніше варто додати:

| Error Code | Suggested HTTP Status | When To Use |
|---|---:|---|
| `INSUFFICIENT_BALANCE` | `409` | Client не має достатньо коштів для escrow hold. |
| `ESCROW_ALREADY_HELD` | `409` | Escrow hold уже створений для contract. |
| `ESCROW_ALREADY_RELEASED` | `409` | Кошти вже були released. |
| `INVALID_PAYMENT_STATE` | `409` | Payment transition не дозволений з поточного status. |

## Implementation Rules

- Services should raise `AppError` subclasses, not return raw `JSONResponse`.
- Routers should stay thin: receive request, call service, return schema.
- Business rule violations should usually be `ConflictError`.
- Access control failures should be `PermissionDeniedError`.
- Missing resources should be `NotFoundError`.
- Sensitive values must not be included in `message` or `details`.

Do not include these values in errors:

- passwords;
- JWT tokens;
- private keys;
- AES keys;
- plaintext encrypted messages;
- file contents.

## Example

Service code:

```python
if task.creator_id == current_user.id:
    raise ConflictError(
        "Cannot create offer for your own task",
        details={"task_id": str(task.id)},
    )
```

API response:

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Cannot create offer for your own task",
    "details": {
      "task_id": "3f4d4d6e-8e2d-4bb2-a6c8-9dfd2f4bce10"
    }
  }
}
```

