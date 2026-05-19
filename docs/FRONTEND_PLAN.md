# Frontend Plan

## Stack

| Технологія | Версія | Роль |
|---|---|---|
| Next.js | 14 (App Router) | Framework, routing, SSR |
| TypeScript | 5 | Типізація |
| Tailwind CSS | 3 | Стилізація |
| Zustand | latest | Глобальний auth стан |
| React Hook Form | latest | Форми |
| Zod | latest | Валідація схем |
| Axios | latest | HTTP клієнт з interceptors |

---

## Структура проєкту

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx          ← сторінка логіну
│   │   │   └── register/
│   │   │       └── page.tsx          ← сторінка реєстрації
│   │   ├── dashboard/
│   │   │   └── page.tsx              ← головна після логіну (захищена)
│   │   ├── layout.tsx                ← root layout з провайдерами
│   │   └── page.tsx                  ← redirect → /login або /dashboard
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx            ← базова кнопка
│   │   │   └── Input.tsx             ← базовий інпут з помилкою
│   │   └── auth/
│   │       ├── LoginForm.tsx         ← форма логіну
│   │       └── RegisterForm.tsx      ← форма реєстрації
│   ├── lib/
│   │   ├── api.ts                    ← axios instance + token interceptor + refresh
│   │   └── tokens.ts                 ← get/set/clear токенів
│   ├── store/
│   │   └── auth.ts                   ← Zustand: user, isAuth, login, logout, fetchMe
│   └── middleware.ts                 ← захист роутів, redirect
├── public/
├── Dockerfile
└── .env.local.example
```

---

## Фази розробки

### Фаза 1: Інфраструктура (поточна)
- [x] Ініціалізація Next.js 14 проєкту
- [x] Встановлення залежностей (axios, zustand, react-hook-form, zod)
- [ ] Dockerfile для фронтенду
- [ ] Додати frontend сервіс в docker-compose
- [ ] Налаштувати Nginx проксі: `/api/*` → FastAPI, `/*` → Next.js

### Фаза 2: Auth інфраструктура
- [ ] `lib/tokens.ts` — зберігання токенів (access в memory, refresh в localStorage)
- [ ] `lib/api.ts` — axios instance з Bearer interceptor та auto-refresh при 401
- [ ] `store/auth.ts` — Zustand store з user, isAuth, login(), logout(), fetchMe()
- [ ] `middleware.ts` — захист роутів

### Фаза 3: UI компоненти
- [ ] `components/ui/Button.tsx` — варіанти: primary, secondary, loading стан
- [ ] `components/ui/Input.tsx` — label, error message, disabled стан

### Фаза 4: Сторінки Login / Register
- [ ] `RegisterForm.tsx` — email + password + confirm, Zod валідація
- [ ] `LoginForm.tsx` — email + password, Zod валідація
- [ ] `/register/page.tsx` — сторінка з формою
- [ ] `/login/page.tsx` — сторінка з формою
- [ ] `/dashboard/page.tsx` — заглушка з user info та logout

### Фаза 5: Docker інтеграція
- [ ] Dockerfile для production (multi-stage)
- [ ] docker-compose.yml — додати frontend сервіс
- [ ] Nginx конфіг — проксі на frontend і API

---

## API контракт (accounts)

Базовий URL: `http://localhost/api` (через Nginx)

### POST /accounts/register
```json
Request:  { "email": "user@example.com", "password": "secret123" }
Response: { "id": 1, "email": "...", "system_role": "user", "created_at": "..." }
Status:   201 Created | 409 Conflict (email зайнятий) | 422 Validation error
```

### POST /accounts/login
```json
Request:  { "email": "user@example.com", "password": "secret123" }
Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
Status:   200 OK | 401 Unauthorized
```

### POST /accounts/refresh
```json
Request:  { "refresh_token": "..." }
Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
Status:   200 OK | 401 Unauthorized
```

### POST /accounts/logout
```json
Request:  { "refresh_token": "..." }
Status:   204 No Content
```

### GET /accounts/me
```
Headers:  Authorization: Bearer <access_token>
Response: { "id": 1, "email": "...", "system_role": "user", ... }
Status:   200 OK | 401 Unauthorized
```

---

## Auth Flow

```
Реєстрація:
  RegisterForm → POST /register → auto POST /login → save tokens → /dashboard

Логін:
  LoginForm → POST /login → save tokens → fetchMe() → /dashboard

Кожен запит:
  axios interceptor → додає Authorization: Bearer <access_token>

При 401:
  axios interceptor → POST /refresh → оновлює токени → повторює запит
  якщо refresh теж 401 → clearTokens() → redirect /login

Logout:
  POST /logout (з refresh_token) → clearTokens() → redirect /login

На mount (layout.tsx):
  fetchMe() → якщо 401 → redirect /login
```

---

## Nginx роутинг (фінальна конфігурація)

```nginx
location /api/ {
    proxy_pass http://api:8000/;
}

location / {
    proxy_pass http://frontend:3000;
}
```

---

## Environment Variables

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost/api
```

У Docker: `NEXT_PUBLIC_API_URL` передається через environment в docker-compose.
