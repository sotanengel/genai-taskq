.PHONY: lint typecheck test unit integration e2e run-api run-worker ci

lint:
	ruff check src tests
	ruff format --check src tests

typecheck:
	mypy src

unit:
	pytest -q tests/unit

integration:
	pytest -q tests/integration

e2e:
	pytest -q tests/e2e

test: unit integration e2e

run-api:
	uvicorn genai_taskq.api.app:app --reload

run-worker:
	gtq-worker

ci: lint typecheck test
