.PHONY: setup test lint format docker-up

setup:
	@echo "Setting up development environment..."
	# Backend setup
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip
	# Frontend setup
	# cd frontend && npm install

test:
	@echo "Running tests..."
	cd backend && . .venv/bin/activate && pytest

lint:
	@echo "Running linting..."
	cd backend && . .venv/bin/activate && ruff check .

format:
	@echo "Formatting code..."
	cd backend && . .venv/bin/activate && ruff format .

docker-up:
	@echo "Starting local docker stack..."
	docker-compose up -d
