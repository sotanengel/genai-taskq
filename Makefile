.PHONY: lint typecheck test unit integration e2e run-api run-worker ci docker-up docker-down docker-logs autostart-install autostart-uninstall preflight-ports

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

preflight-ports:
	./scripts/dev/preflight_ports.sh

docker-up: preflight-ports
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f --tail=200

autostart-install:
	./scripts/dev/bootstrap_launchd.sh install

autostart-uninstall:
	./scripts/dev/bootstrap_launchd.sh uninstall
