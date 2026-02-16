.PHONY: up down logs migrate migration seed test lint format

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec backend python -m app.scripts.seed_data

test:
	docker compose exec backend pytest -v

lint:
	docker compose exec backend ruff check app/

format:
	docker compose exec backend ruff format app/

shell-db:
	docker compose exec db psql -U bloom -d bloom

shell-backend:
	docker compose exec backend bash
