# Tech Stack

## Backend

### Python

Основна мова backend-розробки. Python добре підходить для швидкої реалізації API, криптографічних операцій, прототипування й інтеграції з security tooling.

### FastAPI

Web framework для побудови REST API. Обраний через високу швидкість, автоматичну OpenAPI-документацію, зручну роботу з Pydantic і dependency injection.

Використання в проєкті:

- API endpoints у доменних модулях;
- authorization dependencies;
- request/response validation;
- Swagger/OpenAPI для демонстрації лабораторного MVP.

### Uvicorn

ASGI server для запуску FastAPI-застосунку.

## Project Structure Support

Проєкт організований як FastAPI modular monolith:

```text
core       -> config, exceptions, middleware, logging
database   -> SQLAlchemy base/session/transactions
common     -> shared enums, responses, pagination, validators
modules    -> accounts, marketplace, contracts, communication, delivery, payments, moderation, security, audit
```

## Data Layer

### PostgreSQL

Основна реляційна база даних. Обрана через надійність, транзакційність, індекси, constraints і добру підтримку складних зв'язків.

Зберігає users, tasks, offers, contracts, messages metadata, file metadata, escrow transactions, disputes і audit logs.

### SQLAlchemy

ORM і database toolkit для роботи з PostgreSQL. Дозволяє описувати таблиці як Python models, будувати queries і тримати database layer структурованим.

### Alembic

Migration tool для керування змінами структури БД. Дає можливість створювати versioned migrations і синхронізувати схему БД між різними середовищами.

## Validation and Schemas

### Pydantic

Бібліотека для валідації request/response models у FastAPI.

### Annotated

Python typing utility, який зручно використовувати у FastAPI для залежностей, path/query параметрів і валідаційних обмежень.

## Security and Cryptography

### cryptography

Основна бібліотека для криптографічних операцій:

- AES-GCM encryption/decryption у `modules/security/aes_gcm.py`;
- RSA-OAEP key wrapping окремою RSA encryption key pair у `modules/security/rsa_oaep.py`;
- RSA-PSS signatures окремою RSA signing key pair у `modules/security/rsa_pss.py`;
- secure random key generation;
- key serialization.

### hashlib

Стандартна Python-бібліотека для hashing. У проєкті використовується для SHA-256 fingerprint/hash файлів і payload metadata.

### hmac

Може використовуватись для HMAC-SHA256 у допоміжних сценаріях, але основний authenticated encryption режим — AES-GCM.

### passlib або pwdlib

Бібліотека для password hashing. Рекомендовано використовувати Argon2 або bcrypt.

### python-jose або PyJWT

Бібліотека для створення й перевірки JWT tokens.

## File Storage

### Local File Storage

MVP-сховище encrypted chunks у локальній директорії. Реалізується через `modules/delivery/local_storage.py`.

### S3-compatible Storage

Production-ready підхід. Може бути реалізований через Amazon S3 або MinIO. Інтерфейс передбачається через `modules/delivery/storage_interface.py`, а майбутня реалізація через `modules/delivery/s3_storage.py`.

## Optional Infrastructure

### Redis

Не обов'язковий для MVP, але корисний для token blacklist, rate limiting, caching, websocket/session state і background coordination.

### Celery або RQ

Може використовуватись для background jobs: antivirus scan, async file verification, notification delivery, scheduled cleanup.

### Bandit

Static Application Security Testing tool для Python. Підходить до лабораторної ролі Network Security & Monitoring Engineer.

### Pytest

Основний test framework для unit, integration, crypto verification і API tests.

## Recommended MVP Stack

```text
Python
FastAPI
Uvicorn
PostgreSQL
SQLAlchemy
Alembic
Pydantic
cryptography
hashlib
PyJWT or python-jose
passlib/pwdlib
pytest
bandit
```
