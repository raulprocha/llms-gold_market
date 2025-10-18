FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

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

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cu121

RUN pip install --no-cache-dir \
    transformers==4.37.2 \
    peft==0.10.0 \
    sentencepiece \
    safetensors \
    protobuf \
    pandas \
    boto3 \
    beautifulsoup4 \
    tqdm

WORKDIR /app

ENTRYPOINT ["python"]
