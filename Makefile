.PHONY: dev run test lint docker
dev:
	pip install -r requirements.txt -r requirements-dev.txt
run:
	uvicorn main:app --reload --port 8000
test:
	pytest -q
lint:
	black --check . && isort --check-only . && flake8 .
docker:
	docker build -t explainer-mvp .
