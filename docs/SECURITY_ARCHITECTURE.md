# Security Architecture

## Security Goals

Основні цілі безпеки:

- Конфіденційність повідомлень між client і freelancer.
- Конфіденційність файлів, які передаються в межах contract.
- Перевірка цілісності повідомлень, файлів і критичних подій.
- Захист escrow-операцій від підміни суми, отримувача або статусу.
- Контроль доступу до tasks, contracts, messages, files і disputes.
- Audit trail для розслідування спорів і security incidents.

## Security Module Structure

Криптографічна логіка знаходиться в `modules/security/`.

```text
modules/security/
  aes_gcm.py
  rsa_oaep.py
  rsa_pss.py
  hashing.py
  key_management.py
  crypto_schemas.py
```

- `aes_gcm.py` — AES-GCM encryption/decryption для повідомлень і chunks.
- `rsa_oaep.py` — RSA-OAEP key wrapping для AES data keys.
- `rsa_pss.py` — RSA-PSS digital signatures і signature verification.
- `hashing.py` — SHA-256 для файлів і payload fingerprints.
- `key_management.py` — генерація двох RSA key pairs, key rotation, key metadata.
- `crypto_schemas.py` — структури encrypted payload, encrypted key і signature metadata.

`security` є технічним модулем. Він не містить бізнес-правил і не вирішує, хто є client або freelancer.

## Chosen Cryptographic Design

Основний підхід:

```text
AES-GCM + RSA-OAEP + RSA-PSS + SHA-256 + key separation
```

### AES-GCM

AES-GCM використовується для шифрування повідомлень і файлів. Це authenticated encryption mode, який одночасно забезпечує конфіденційність і перевірку цілісності через authentication tag.

Переваги AES-GCM:

- швидкий режим шифрування;
- не потребує окремого HMAC для базового integrity check;
- добре підтримується бібліотекою `cryptography`;
- підходить для API payloads і file chunks;
- зменшує ризик помилок порівняно з AES-CBC + HMAC.

### RSA-OAEP

RSA-OAEP використовується тільки для шифрування AES-ключів. Самі повідомлення і файли не шифруються напряму через RSA, тому що RSA не підходить для великих payloads.

```text
Data -> encrypted with AES-GCM
AES key -> encrypted with recipient RSA-OAEP public key
```

### RSA-PSS

RSA-PSS використовується тільки для цифрового підпису критичних подій і metadata.

Приклади подій:

- створення contract;
- escrow hold;
- escrow release;
- escrow refund;
- dispute decision;
- final file submission metadata.

### SHA-256

SHA-256 використовується для fingerprint і hash verification файлів або metadata. SHA-256 сам по собі не є механізмом автентифікації. Для захисту від підміни основну роль виконує AES-GCM tag або digital signature.

## Key Separation

Кожен користувач має дві окремі RSA key pairs:

```text
rsa_encryption -> RSA-OAEP key wrapping
rsa_signing    -> RSA-PSS digital signatures
```

Це важливо, тому що один ключ не повинен використовуватись для різних криптографічних цілей. Key separation зменшує ризик криптографічних помилок, спрощує rotation і дозволяє відкликати signing key без впливу на encryption flow.

## Why AES-GCM Instead of AES-CBC/CTR + HMAC

### AES-CBC + HMAC

Це класичний підхід, але він складніший у реалізації. Потрібно правильно працювати з padding, IV, порядком перевірки MAC і окремими ключами.

Основні ризики:

- padding oracle vulnerabilities при неправильній реалізації;
- необхідність verify-before-decrypt;
- більша кількість деталей, у яких легко помилитися.

### AES-CTR + HMAC

CTR швидкий і зручний для потокового шифрування, але критично важливо ніколи не повторювати nonce з тим самим ключем. Також потрібно окремо реалізувати HMAC.

### AES-GCM

AES-GCM є рекомендованим для цього проєкту, тому що він швидкий, сучасний і поєднує encryption та integrity check в одному режимі.

## Message Encryption

Звичайні communication messages шифруються одним AES-GCM operation, тому що вони мають малий розмір.

Структура encrypted message metadata:

```json
{
  "message_id": "uuid",
  "contract_id": "uuid",
  "sender_id": "uuid",
  "recipient_id": "uuid",
  "algorithm": "AES-GCM",
  "nonce": "base64",
  "ciphertext": "base64",
  "tag": "base64",
  "encrypted_key": "base64",
  "created_at": "timestamp"
}
```

У практичній реалізації `cryptography` може повертати ciphertext і tag разом, але в документації tag виділяється окремо для зрозумілості.

## File Encryption

Файли шифруються chunk-based підходом у модулі `delivery` з використанням crypto-функцій із `security`.

Правила:

- default chunk size: `1 MB`;
- кожен chunk шифрується окремо через AES-GCM;
- кожен chunk має унікальний nonce;
- для всього файлу зберігається SHA-256 hash;
- metadata файлу може бути підписана RSA-PSS.

Структура chunk metadata:

```json
{
  "file_id": "uuid",
  "chunk_index": 0,
  "algorithm": "AES-GCM",
  "nonce": "base64",
  "ciphertext_path": "storage/path",
  "tag": "base64",
  "chunk_size": 1048576,
  "created_at": "timestamp"
}
```

## Key Management

Для MVP передбачається така модель:

- кожен користувач має дві окремі RSA key pairs: encryption key pair для RSA-OAEP і signing key pair для RSA-PSS;
- public keys зберігаються в системі окремо для encryption і signing;
- private keys не повинні зберігатися у відкритому вигляді;
- AES data keys генеруються для message session або file upload;
- AES key шифрується через RSA-OAEP public key отримувача з encryption key pair;
- key metadata зберігається окремо від encrypted payload.

Production-ready покращення:

- використання KMS;
- rotation ключів;
- hardware-backed secrets;
- envelope encryption;
- audit key access.

## Integrity and Authenticity

Integrity забезпечується кількома рівнями:

- AES-GCM authentication tag для кожного message або chunk.
- SHA-256 для перевірки фінального файлу після збірки chunks.
- RSA-PSS signature для critical event metadata.
- Audit log для незаперечності бізнес-подій.

## Access Control

Система використовує JWT + RBAC + ownership checks.

Базові правила:

- тільки автор task може редагувати task до створення contract;
- тільки учасники contract можуть читати communication messages і delivery files;
- тільки client може підтвердити завершення роботи;
- тільки moderator може вирішити dispute;
- admin має системні права, але його дії також логуються.

## Audit Logging

Audit log має фіксувати:

- login events;
- task price changes;
- offer acceptance;
- contract confirmation;
- escrow hold/release/refund;
- file submission;
- dispute creation;
- dispute resolution;
- failed integrity verification.

Audit record повинен містити:

```text
actor_id
entity_type
entity_id
action
payload_hash
signature
created_at
```

## Security Defaults

- Passwords зберігаються тільки у вигляді Argon2 або bcrypt hash.
- JWT access token має короткий lifetime.
- Refresh token має довший lifetime і може відкликатися.
- AES-GCM nonce ніколи не повторюється з тим самим key.
- Sensitive payloads не логуються у відкритому вигляді.
- Failed decryption або failed integrity check призводить до відхилення payload.
