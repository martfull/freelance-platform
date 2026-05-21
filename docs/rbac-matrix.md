# RBAC Matrix

## Архітектура

RBAC у проєкті двошаровий:

1. **System Role** — записана в `users.system_role`, перевіряється через `require_role()` dep в `permissions.py`
2. **Contextual Role** — визначається участю в конкретному контракті (`client` або `freelancer`), перевіряється на рівні service

---

## System Roles

Три системні ролі визначені в `SystemRole(StrEnum)` (`common/enums.py`):

| Role | Опис |
|---|---|
| `user` | Звичайний зареєстрований користувач (дефолт) |
| `moderator` | Може розглядати диспути і читати audit log |
| `admin` | Повний доступ до адміністрування |

---

### Accounts 

| Endpoint | Публічний | user | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `POST /accounts/register` | ✓ | — | — | — |
| `POST /accounts/login` | ✓ | — | — | — |
| `POST /accounts/refresh` | ✓ | — | — | — |
| `POST /accounts/logout` | ✓ | — | — | — |
| `GET /accounts/me` | — | ✓ | ✓ | ✓ |
| `POST /accounts/keys` | — | ✓ | ✓ | ✓ |
| `GET /accounts/me/keys` | — | ✓ | ✓ | ✓ |
| `GET /accounts/users/{id}/keys/public` | — | ✓ | ✓ | ✓ |

### Marketplace 

| Endpoint | Публічний | user | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `GET /marketplace/tasks` | ✓ | — | — | — |
| `GET /marketplace/tasks/{id}` | ✓ | — | — | — |
| `POST /marketplace/tasks` | — | ✓ | — | — |
| `PATCH /marketplace/tasks/{id}` | — | own | — | ✓ |
| `DELETE /marketplace/tasks/{id}` | — | own | — | ✓ |
| `GET /marketplace/tasks/{id}/offers` | — | own task | — | — |
| `POST /marketplace/tasks/{id}/offers` | — | ✓ | — | — |
| `POST /marketplace/offers/{id}/accept` | — | own task | — | — |
| `POST /marketplace/offers/{id}/withdraw` | — | own offer | — | — |

### Contracts 

| Endpoint | client | freelancer | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `GET /contracts/my` | ✓ | ✓ | — | — |
| `GET /contracts/{id}` | ✓ | ✓ | — | — |
| `POST /contracts/{id}/confirm` | ✓ | ✓ | — | — |
| `POST /contracts/{id}/cancel` | ✓ | ✓ | — | — |

### Communication 

| Endpoint | client | freelancer | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `GET /communication/{contract_id}/messages` | ✓ | ✓ | ✓ | ✓ |
| `POST /communication/{contract_id}/messages` | ✓ | ✓ | — | — |

### Delivery 

| Endpoint | client | freelancer | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `POST /delivery/{contract_id}/upload` | — | ✓ | — | — |
| `GET /delivery/{contract_id}/files` | ✓ | ✓ | — | — |
| `GET /delivery/{contract_id}/files/{id}` | ✓ | ✓ | — | — |
| `POST /delivery/{contract_id}/submit` | — | ✓ | — | — |

### Payments 

| Endpoint | client | freelancer | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| `POST /payments/{contract_id}/deposit` | ✓ | — | — | — |
| `POST /payments/{contract_id}/release` | — | — | ✓ | ✓ |
| `GET /payments/{contract_id}/ledger` | ✓ | ✓ | ✓ | ✓ |

### Moderation 

| Endpoint | user | moderator | admin |
|---|:---:|:---:|:---:|
| `POST /moderation/disputes` | own contract | — | — |
| `GET /moderation/disputes` | own | ✓ | ✓ |
| `POST /moderation/disputes/{id}/resolve` | — | ✓ | ✓ |

### Audit 

| Endpoint | user | moderator | admin |
|---|:---:|:---:|:---:|
| `GET /audit/logs` | — | ✓ | ✓ |
| `GET /audit/logs/{id}/verify` | — | ✓ | ✓ |

---
