# System Architecture

## Overview

This system implements a multi-stage ML pipeline for predicting gold market movements from financial news using Large Language Models.

## Components

### 1. Data Collection Layer
- **News API Integration**: Alpaca Markets API for real-time financial news
- **Market Data**: MetaTrader 5 for XAU/USD candlestick data
- **Storage**: AWS S3 for raw and processed data

### 2. Preprocessing Pipeline

#### Headline Rewriting (Mistral-7B)
- **Purpose**: Standardize news headlines to emphasize gold market relevance
- **Model**: Mistral-7B-Instruct-v0.2 (inference mode)
- **Input**: Raw financial headlines + context
- **Output**: Gold-focused rewritten headlines
- **Infrastructure**: SageMaker Processing (ml.g4dn.xlarge)

#### Sentiment Analysis (FinBERT)
- **Purpose**: Extract sentiment and confidence scores
- **Model**: yiyanghkust/finbert-tone
- **Classes**: Positive, Neutral, Negative
- **Intensity**: Weak, Moderate, Strong (based on confidence)
- **Infrastructure**: SageMaker Processing (ml.g4dn.xlarge)

### 3. Feature Engineering
- **Platform**: AWS Athena (SQL queries)
- **Features**:
  - Temporal alignment (30-min candles)
  - Price reference calculation
  - Correlated assets (ETFs, indices)
  - Technical indicators
  - Market context variables

### 4. Model Training

#### Fine-tuning Pipeline
- **Base Model**: Mistral-7B-Instruct-v0.2
- **Method**: LoRA (Low-Rank Adaptation)
  - r=16, alpha=32, dropout=0.05
  - 4-bit quantization (QLoRA)
- **Training Data**: ~27K labeled examples
- **Labels**: 
  - Direction: Up/Down/Neutral
  - Magnitude: Low/Medium-Low/Medium-High/High
  - Horizons: 6h, 12h, 24h, 48h
- **Infrastructure**: SageMaker Training (ml.g5.2xlarge or ml.g5.12xlarge)
- **Optimization**:
  - Learning rate: 1.5e-4
  - Batch size: 16 (with gradient accumulation)
  - Epochs: 3
  - Early stopping enabled

### 5. Inference Pipeline
- **Input**: New financial headline + market context
- **Processing**: Rewrite → Sentiment → Feature extraction
- **Prediction**: JSON output with multi-horizon forecasts
- **Latency**: ~100ms per headline
- **Infrastructure**: SageMaker Endpoint (ml.g4dn.xlarge)

## Data Flow

```
┌─────────────┐
│  News API   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Headline        │
│ Rewriter        │
│ (Mistral-7B)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Sentiment       │
│ Analysis        │
│ (FinBERT)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ Feature         │◄─────┤ Market Data  │
│ Engineering     │      │ (MT5)        │
│ (Athena)        │      └──────────────┘
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Fine-tuned      │
│ Mistral Model   │
│ (Prediction)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Trading Signal  │
│ (JSON Output)   │
└─────────────────┘
```

## AWS Services

| Service | Purpose | Cost Impact |
|---------|---------|-------------|
| SageMaker Training | Model fine-tuning | High (GPU hours) |
| SageMaker Processing | Batch inference | Medium |
| SageMaker Endpoints | Real-time inference | Medium (if deployed) |
| S3 | Data storage | Low |
| ECR | Docker registry | Low |
| Athena | SQL queries | Low (pay-per-query) |
| CloudWatch | Monitoring | Low |

## Scalability Considerations

### Horizontal Scaling
- Multi-instance training for larger datasets
- Distributed inference with SageMaker batch transform
- S3 partitioning for efficient data access

### Vertical Scaling
- Instance type selection based on workload:
  - Development: ml.t3.medium
  - Production inference: ml.g4dn.xlarge
  - Production training: ml.g5.2xlarge - ml.g5.12xlarge

### Cost Optimization
- Spot instances for training (up to 70% savings)
- S3 lifecycle policies for old data
- Inference batching to reduce API calls
- Model quantization (4-bit) reduces memory

## Security

- IAM roles with least privilege
- VPC isolation for SageMaker jobs
- Encrypted S3 buckets
- Secrets Manager for API tokens
- CloudTrail for audit logging

## Monitoring

- CloudWatch metrics for job status
- Custom metrics for model performance
- Alerting on job failures
- Cost tracking per pipeline stage

## Disaster Recovery

- Model checkpoints saved to S3
- Versioned datasets
- Infrastructure as Code (Docker, scripts)
- Automated backup policies
