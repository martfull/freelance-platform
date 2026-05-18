.PHONY: build up down logs nginx-logs migrate migration downgrade db-reset test test-v lint bandit

build:
	docker compose up --build -d

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api

nginx-logs:
	docker compose logs -f nginx

migrate:
	docker compose exec api alembic upgrade head

migration:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

downgrade:
	docker compose exec api alembic downgrade -1

db-reset:
	docker compose down -v
	docker compose up -d
	sleep 3
	docker compose exec api alembic upgrade head

test:
	docker compose exec api pytest tests/ -v --cov=app --cov-report=term-missing

test-v:
	docker compose exec api pytest tests/ -v

lint:
	docker compose exec api flake8 app/ --max-line-length=120

bandit:
	docker compose exec api bandit -r app/ -f html -o /app/security/reports/bandit-report.html || true
	docker compose exec api bandit -r app/ -f json -o /app/security/reports/bandit-report.json || true
	docker compose exec api bandit -r app/ -ll -ii
