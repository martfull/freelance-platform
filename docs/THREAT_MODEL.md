# Threat Model

## Overview

Threat model описує основні активи системи, потенційних порушників, загрози конфіденційності, цілісності й доступності, а також базові методи захисту.

## Assets

| ID | Asset | Description | Sensitivity |
|---|---|---|---|
| A1 | User Accounts | Email, password hash, profile data | High |
| A2 | Tasks and Offers | Опис задач, бюджети, пропозиції | Medium |
| A3 | Communication Messages | Приватна комунікація client/freelancer | High |
| A4 | Delivery Files | Результати роботи, архіви, документи | High |
| A5 | Payment and Escrow Records | Баланси, hold/release/refund transactions | Critical |
| A6 | Cryptographic Keys | RSA encryption/signing keys, AES key metadata | Critical |
| A7 | Audit Logs | Security-relevant event history | High |
| A8 | Moderation Evidence | Матеріали спорів і рішення модерації | High |

## Threat Actors

| Actor | Description | Motivation |
|---|---|---|
| External Attacker | Неавторизований користувач з інтернету | Викрадення даних, підміна платежів |
| Malicious User | Зареєстрований користувач платформи | Шахрайство, доступ до чужих contracts |
| Malicious Client | Замовник, який не хоче платити | Блокування release, фальшивий dispute |
| Malicious Freelancer | Виконавець, який хоче отримати оплату без роботи | Підробка submission або доказів |
| Compromised Moderator | Модератор з неправомірними діями | Нечесне рішення dispute |
| Network Attacker | Атакує канал передачі | Перехоплення або зміна payloads |

## CIA Threats

| Asset | Confidentiality Threat | Integrity Threat | Availability Threat |
|---|---|---|---|
| User Accounts | Викрадення облікових даних | Зміна email або ролі | Масовий login abuse |
| Communication Messages | Читання приватних повідомлень | Підміна ciphertext або metadata | Блокування доступу до комунікації |
| Delivery Files | Несанкціонований download | Зміна chunks або final file | Втрата файлів у storage |
| Payment Records | Перегляд фінансових даних | Підміна amount або receiver | Неможливість release/refund |
| Crypto Keys | Викрадення private keys | Підміна public key | Key service unavailable |
| Audit Logs | Розкриття sensitive events | Видалення або зміна logs | Неможливість investigation |

## Risk Matrix

| Threat | Object | Probability | Impact | Risk | Mitigation |
|---|---|---:|---:|---:|---|
| Message interception | Communication messages | 3 | 5 | 15 | AES-GCM encryption, TLS |
| File tampering | Delivery files | 3 | 5 | 15 | AES-GCM tag, SHA-256 final hash |
| Escrow amount manipulation | Payment records | 2 | 5 | 10 | DB constraints, signatures, audit logs |
| Unauthorized contract access | Contracts/messages/files | 3 | 4 | 12 | JWT, ownership checks |
| Password compromise | User accounts | 3 | 5 | 15 | Argon2/bcrypt, rate limiting, 2FA future |
| Private key leakage | Crypto keys | 2 | 5 | 10 | No plaintext private key storage, KMS future |
| Moderator abuse | Moderation decisions | 2 | 4 | 8 | Audit logs, admin review |
| Storage data loss | File chunks | 2 | 4 | 8 | Backups, object storage lifecycle |
| Replay attack | Messages/events | 2 | 4 | 8 | Nonce, timestamp, audit event IDs |
| API abuse | Public endpoints | 4 | 3 | 12 | Rate limiting, validation, logging |

## Key Mitigations

- TLS для всіх network connections.
- AES-GCM для confidentiality та integrity encrypted data.
- RSA-OAEP для secure AES key wrapping.
- RSA-PSS для critical event signatures.
- Key separation: окремі RSA key pairs для encryption і signing.
- SHA-256 для file fingerprint verification.
- JWT + RBAC + ownership checks.
- Argon2 або bcrypt для password hashing.
- Audit logs для critical actions.
- Rate limiting для auth і public endpoints.
- Bandit SAST для Python security checks.

## Abuse Cases

### User tries to accept own task

Expected behavior: API returns `409 Conflict` або `403 Forbidden`. Система не дозволяє створити contract, де client і freelancer мають однаковий `user_id`.

### Attacker changes encrypted message payload

Expected behavior: AES-GCM verification fails. Message is rejected and event is logged.

### Attacker modifies file chunk

Expected behavior: chunk decryption fails або final SHA-256 не збігається. File is marked as `rejected` або `failed`.

### Client refuses to confirm completed work

Expected behavior: freelancer opens dispute. Moderator reviews evidence and decides release/refund.

### User tries to access another contract communication

Expected behavior: ownership check fails, API returns `403 Forbidden`.

## Security Testing

Recommended checks:

- Bandit scan for Python code.
- Unit tests for crypto functions.
- API tests for authorization boundaries.
- Tests for tampered ciphertext and chunks.
- Tests for payments state transitions.
- Tests for moderation role restrictions.
