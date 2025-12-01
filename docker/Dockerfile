# Base Docker image for all ML pipelines
# Optimized for GPU-accelerated NLP workloads on AWS SageMaker

FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04

LABEL maintainer="Raul Rocha <raulrocha.rpr@gmail.com>"
LABEL description="Production ML pipeline for financial NLP with LLMs"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/opt/ml/cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create Python symlink
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Install ML/NLP dependencies
RUN pip install --no-cache-dir \
    transformers==4.37.2 \
    peft==0.10.0 \
    sentencepiece \
    safetensors \
    protobuf \
    pandas \
    boto3 \
    beautifulsoup4 \
    tqdm \
    python-dotenv \
    sagemaker

WORKDIR /app

ENTRYPOINT ["python"]
