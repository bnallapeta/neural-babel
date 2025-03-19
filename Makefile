.PHONY: setup-local run-local run-mock run-real test lint clean build push deploy

# Variables
PYTHON := python3
PIP := pip3
REGISTRY_URL ?= localhost:5000
IMAGE_NAME := neural-babel
IMAGE_TAG ?= latest
FULL_IMAGE_NAME := $(REGISTRY_URL)/$(IMAGE_NAME):$(IMAGE_TAG)
K8S_NAMESPACE ?= default

# Development
setup-local:
	$(PIP) install -r requirements.txt

run-local: run-mock

run-mock:
	bash run_services_mock.sh

run-real:
	@echo "Running real services is recommended in separate terminals:"
	@echo " - Terminal 1: ./run_asr.sh"
	@echo " - Terminal 2: ./run_translation.sh"
	@echo " - Terminal 3: ./run_tts.sh"
	@echo " - Terminal 4: ./run_neural_babel.sh"
	@echo "See README-run-services.md for more information."

# Testing
test:
	pytest tests/ --cov=src --cov-report=term-missing

lint:
	flake8 src/ tests/

# Cleaning
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# Docker
build:
	docker build -t $(FULL_IMAGE_NAME) .

push:
	docker push $(FULL_IMAGE_NAME)

# Kubernetes
deploy:
	kubectl apply -f k8s/configmap.yaml -n $(K8S_NAMESPACE)
	kubectl apply -f k8s/deployment.yaml -n $(K8S_NAMESPACE)
	kubectl apply -f k8s/service.yaml -n $(K8S_NAMESPACE)
	kubectl apply -f k8s/ingress.yaml -n $(K8S_NAMESPACE)

# Help
help:
	@echo "Available targets:"
	@echo "  setup-local  - Install dependencies locally"
	@echo "  run-local    - Run the application locally using mock services (alias for run-mock)"
	@echo "  run-mock     - Run the application with mock services"
	@echo "  run-real     - Show instructions for running the application with real services"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting"
	@echo "  clean        - Clean temporary files"
	@echo "  build        - Build Docker image"
	@echo "  push         - Push Docker image to registry"
	@echo "  deploy       - Deploy to Kubernetes"
	@echo "  help         - Show this help message"

# Default target
.DEFAULT_GOAL := help 