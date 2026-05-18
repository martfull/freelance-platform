.PHONY: build up down logs migrate migration downgrade db-reset test test-v lint bandit

build:
	docker compose up --build -d

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api

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
	docker compose exec api pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing

test-v:
	docker compose exec api pytest backend/tests/ -v

lint:
	docker compose exec api flake8 backend/ --max-line-length=120

bandit:
	docker compose exec api bandit -r backend/ -f html -o security/reports/bandit-report.html || true
	docker compose exec api bandit -r backend/ -f json -o security/reports/bandit-report.json || true
	docker compose exec api bandit -r backend/ -ll -ii
