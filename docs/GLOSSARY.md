# Glossary

## AES-GCM

Symmetric encryption mode, який забезпечує одночасно confidentiality і integrity. У проєкті використовується для шифрування communication messages і file chunks.

## RSA-OAEP

Asymmetric encryption padding scheme. У проєкті використовується тільки для шифрування AES keys через public key отримувача. Реалізується в `modules/security/rsa_oaep.py`.

## RSA-PSS

Digital signature scheme. Використовується тільки для підпису critical events і metadata. Реалізується в `modules/security/rsa_pss.py`.

## Key Separation

Принцип, за яким різні криптографічні задачі використовують різні ключі. У проєкті є окрема RSA key pair для encryption (`rsa_encryption`) і окрема RSA key pair для signing (`rsa_signing`).

## SHA-256

Cryptographic hash function. У проєкті використовується для file fingerprint і payload hash.

## Escrow

Механізм, при якому кошти client-а тимчасово блокуються системою і переходять freelancer-у тільки після завершення роботи або рішення moderator.

## Simulated Escrow

MVP-версія escrow без реальних платежів. Баланси і транзакції існують як записи в PostgreSQL.

## Task

Публікація користувача з описом роботи, бюджетом і вимогами.

## Offer

Пропозиція виконавця виконати task.

## Contract

Активна домовленість між client і freelancer після прийняття offer і підтвердження сторін.

## Client

Користувач, який створив task і оплачує роботу. Це контекстна роль, а не окремий тип акаунта.

## Freelancer

Користувач, який прийняв task і виконує contract. Це контекстна роль, а не окремий тип акаунта.

## Moderator

Привілейований користувач, який розглядає disputes і може ухвалити release/refund decision.

## Chunk

Частина великого файлу. У проєкті файли діляться на chunks по 1 MB, і кожен chunk шифрується окремо.

## Nonce

Унікальне значення, яке використовується в AES-GCM. Для одного AES key nonce не повинен повторюватися.

## Authentication Tag

Значення, яке створюється AES-GCM і використовується для перевірки, що ciphertext або metadata не були змінені.

## RBAC

Role-Based Access Control. Модель контролю доступу, де permissions залежать від ролей користувача.

## Ownership Check

Перевірка, чи користувач має відношення до конкретного ресурсу, наприклад є client або freelancer у певному contract.

## Audit Log

Журнал security-relevant подій, який використовується для розслідування спорів, перевірки escrow-операцій і аналізу інцидентів.
