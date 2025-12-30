# Makefile for PyATS Show Command API

.PHONY: help build run dev stop clean logs shell test

# Default target
help:
	@echo "PyATS Show Command API - Make Commands"
	@echo "======================================="
	@echo ""
	@echo "Production:"
	@echo "  make build       - Build production Docker image"
	@echo "  make run         - Run production container"
	@echo "  make stop        - Stop production container"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Run development container with hot-reload"
	@echo "  make dev-build   - Build development Docker image"
	@echo "  make dev-stop    - Stop development container"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs        - View container logs"
	@echo "  make shell       - Open shell in running container"
	@echo "  make clean       - Remove containers and images"
	@echo "  make test        - Run tests (when implemented)"
	@echo ""

# Production targets
build:
	@echo "Building production Docker image..."
	docker-compose build

run:
	@echo "Starting production container..."
	docker-compose up -d
	@echo "API running at http://localhost:8000"
	@echo "Swagger UI: http://localhost:8000/docs"

stop:
	@echo "Stopping production container..."
	docker-compose down

# Development targets
dev-build:
	@echo "Building development Docker image..."
	docker-compose -f docker-compose.dev.yml build

dev:
	@echo "Starting development container with hot-reload..."
	docker-compose -f docker-compose.dev.yml up
	@echo "API running at http://localhost:8000"
	@echo "Swagger UI: http://localhost:8000/docs"

dev-stop:
	@echo "Stopping development container..."
	docker-compose -f docker-compose.dev.yml down

# Utility targets
logs:
	docker-compose logs -f

logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f

shell:
	docker exec -it pyats-api /bin/bash

shell-dev:
	docker exec -it pyats-api-dev /bin/bash

clean:
	@echo "Cleaning up containers and images..."
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker rmi pyats-api_pyats-api 2>/dev/null || true
	docker rmi pyats-api_pyats-api-dev 2>/dev/null || true
	@echo "Cleanup complete"

test:
	@echo "Running tests..."
	docker-compose -f docker-compose.dev.yml exec pyats-api-dev pytest tests/ -v

# Quick start for first time users
quickstart:
	@echo "Quick start - Setting up development environment..."
	@make dev-build
	@echo ""
	@echo "Setup complete! Now run:"
	@echo "  make dev"
