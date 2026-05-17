# Secure Freelance Marketplace

**Secure Freelance Marketplace** — це backend-first платформа для безпечної взаємодії між замовниками та виконавцями у freelance-маркетплейсі. Система дозволяє користувачам створювати задачі, переглядати доступні пропозиції, домовлятися через захищений чат, передавати результати роботи у вигляді файлів та використовувати escrow-механізм для безпечної оплати.

Документація написана українською мовою, але назви модулів, API, моделей, таблиць і технічних компонентів використовуються англійською, як у реальному software engineering проєкті.

## Project Goal

Мета проєкту — спроєктувати захищену freelance-платформу з акцентом на криптографічний захист повідомлень, файлів і критичних бізнес-подій. Проєкт знаходиться на стартовій стадії, тому поточна документація описує архітектуру, стек, модель безпеки, базові API, базу даних і майбутній план реалізації.

## Key Features

- Публікація задач із описом, бюджетом і можливістю змінювати ціну до старту contract.
- Перегляд доступних задач іншими користувачами.
- Відгук виконавця на задачу через offer flow.
- Перехід задачі в contract після підтвердження домовленості обома сторонами.
- REST-based encrypted communication між учасниками contract.
- Передача файлів із chunk-based encryption.
- Simulated escrow для блокування, release або refund коштів.
- Moderation flow для спірних ситуацій.
- JWT authentication, RBAC і ownership checks.
- AES-GCM, RSA-OAEP, RSA-PSS, SHA-256 і key separation для захисту даних.

## Architecture Summary

Проєкт використовує архітектурний стиль **modular monolith**. Це один FastAPI backend-застосунок із чітким поділом на технічні модулі (`core`, `database`, `common`) та доменні модулі в `modules/`.

Фінальні доменні модулі:

```text
accounts
marketplace
contracts
communication
delivery
payments
moderation
security
audit
```

## Documentation Map

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) — продуктове бачення і сценарії.
- [ARCHITECTURE.md](ARCHITECTURE.md) — системна архітектура та структура модулів.
- [TECH_STACK.md](TECH_STACK.md) — технологічний стек.
- [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md) — криптографія та безпека.
- [DATABASE_DESIGN.md](DATABASE_DESIGN.md) — проєктування бази даних.
- [API_SPEC.md](API_SPEC.md) — стартова API-специфікація.
- [THREAT_MODEL.md](THREAT_MODEL.md) — модель загроз і ризики.
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — план реалізації.
- [GLOSSARY.md](GLOSSARY.md) — терміни проєкту.
