.PHONY: install test lint typecheck coverage openapi run docker-up docker-down

install:
	python -m pip install -e . pytest hypothesis ruff mypy pytest-cov httpx pre-commit

test:
	python -m pytest

lint:
	ruff check .

typecheck:
	mypy kernel api sdk

coverage:
	python -m pytest --cov=kernel --cov=api --cov=sdk --cov-report=term-missing

openapi:
	python scripts/export_openapi.py

run:
	uvicorn api.main:app --reload

docker-up:
	docker compose up --build

docker-down:
	docker compose down --volumes
