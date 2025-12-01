.PHONY: help install build deploy test clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make build      - Build Docker image"
	@echo "  make deploy     - Deploy image to ECR"
	@echo "  make sentiment  - Run sentiment analysis pipeline"
	@echo "  make train      - Run model training pipeline"
	@echo "  make clean      - Clean temporary files"

install:
	pip install -r requirements.txt

build:
	cd containers/base && docker build -t gold-ml-pipeline:latest .

deploy:
	./deploy.sh

sentiment:
	python containers/sentiment_analysis/run_job.py

train:
	python containers/mistral_finetuning/run_training.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
