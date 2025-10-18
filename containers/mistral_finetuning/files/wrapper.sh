#!/bin/bash

echo "Descompactando code.tar.gz..."
tar -xzf /opt/ml/processing/code/code.tar.gz -C /opt/ml/processing/code/

echo "Rodando process.py..."
python3 /opt/ml/processing/code/process.py
