.PHONY: install run test lint format eval docker-up docker-down

install:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -v --cov=app --cov-report=term-missing

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

eval:
	python -m evals.run_evals

docker-up:
	docker compose up --build

docker-down:
	docker compose down
