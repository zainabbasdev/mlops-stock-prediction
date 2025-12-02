.PHONY: help setup install start stop restart logs clean test format lint docker-build docker-push

# Default target
help:
	@echo "MLOps Project - Available Commands"
	@echo "=================================="
	@echo "setup          - Initial project setup"
	@echo "install        - Install Python dependencies"
	@echo "start          - Start all services"
	@echo "stop           - Stop all services"
	@echo "restart        - Restart all services"
	@echo "logs           - View logs from all services"
	@echo "clean          - Clean up generated files"
	@echo "test           - Run unit tests"
	@echo "test-api       - Test the prediction API"
	@echo "format         - Format code with Black"
	@echo "lint           - Run linters (flake8, pylint)"
	@echo "docker-build   - Build Docker images"
	@echo "docker-push    - Push Docker images to registry"
	@echo "dvc-init       - Initialize DVC"
	@echo "airflow-trigger - Trigger Airflow DAG"

# Setup
setup:
	@echo "Setting up project..."
	@chmod +x scripts/quick_start.sh
	@./scripts/quick_start.sh

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

# Start services
start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Services started!"
	@echo "Airflow UI: http://localhost:8080"
	@echo "MinIO Console: http://localhost:9001"
	@echo "Prediction API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

# Stop services
stop:
	@echo "Stopping all services..."
	docker-compose down

# Restart services
restart:
	@echo "Restarting all services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Clean generated files
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "Cleanup complete!"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=term --cov-report=html

# Test API
test-api:
	@echo "Testing prediction API..."
	python scripts/test_api.py

# Format code
format:
	@echo "Formatting code with Black..."
	black src/ tests/

# Lint code
lint:
	@echo "Running linters..."
	flake8 src/ --max-line-length=100
	pylint src/ --disable=C,R,W

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose build

# Push Docker images (requires login)
docker-push:
	@echo "Pushing Docker images..."
	docker tag mlops-project-prediction-service:latest ${DOCKER_USERNAME}/stock-volatility-predictor:latest
	docker push ${DOCKER_USERNAME}/stock-volatility-predictor:latest

# Initialize DVC
dvc-init:
	@echo "Initializing DVC..."
	python scripts/setup_dvc.py

# Trigger Airflow DAG
airflow-trigger:
	@echo "Triggering Airflow DAG..."
	docker exec -it airflow-webserver airflow dags trigger stock_volatility_pipeline

# Quick development setup
dev-setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	pre-commit install || echo "pre-commit not installed"
	@echo "Development environment ready!"

# Run data extraction
extract-data:
	@echo "Extracting data from API..."
	python src/data/extract.py

# Run data transformation
transform-data:
	@echo "Transforming data..."
	python src/data/transform.py

# Train model
train-model:
	@echo "Training model..."
	python src/models/train.py

# Full pipeline (manual)
pipeline: extract-data transform-data train-model
	@echo "Pipeline complete!"

# Check service health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health || echo "Prediction API: DOWN"
	@curl -s http://localhost:8080/health || echo "Airflow: DOWN"
	@curl -s http://localhost:9000/minio/health/live || echo "MinIO: DOWN"
	@curl -s http://localhost:9090/-/healthy || echo "Prometheus: DOWN"
	@curl -s http://localhost:3000/api/health || echo "Grafana: DOWN"
