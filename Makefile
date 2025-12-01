.PHONY: help install build deploy sentiment train inference clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make build      - Build Docker image"
	@echo "  make deploy     - Deploy image to ECR"
	@echo "  make sentiment  - Run sentiment analysis pipeline"
	@echo "  make train      - Run model training pipeline"
	@echo "  make inference  - Run inference pipeline"
	@echo "  make clean      - Clean temporary files"

install:
	pip install -r requirements.txt

build:
	cd docker && docker build -t gold-ml-pipeline:latest .

deploy:
	./deploy.sh

sentiment:
	python pipelines/sentiment_analysis/run.py

train:
	python pipelines/model_training/run.py

inference:
	python pipelines/inference/run.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
