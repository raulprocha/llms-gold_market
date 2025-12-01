# Financial News Impact Prediction for Gold Markets

Production-ready ML pipeline for predicting XAU/USD price movements using Large Language Models and sentiment analysis on AWS SageMaker.

## Business Value

- **Automated Trading Signals**: Predict gold price direction and magnitude from financial news
- **Multi-Horizon Forecasting**: 6h, 12h, 24h, and 48h prediction windows
- **Scalable Infrastructure**: AWS SageMaker with GPU acceleration
- **Cost-Effective**: LoRA fine-tuning reduces training costs by 90%

## Key Features

- Fine-tuned Mistral-7B for financial text understanding
- FinBERT sentiment analysis specialized for financial news
- Automated headline rewriting for gold market context
- Multi-class prediction: direction (Up/Down/Neutral) + magnitude (4 levels)
- Integrated with market data (ETFs, indices, correlates)

## Architecture

```
News API → Headline Rewriting → Sentiment Analysis → Feature Engineering → LLM Prediction
  (Alpaca)     (Mistral-7B)         (FinBERT)          (SQL/Athena)      (Fine-tuned Mistral)
                    ↓                    ↓                    ↓                    ↓
              AWS SageMaker        AWS SageMaker        AWS Athena          AWS SageMaker
```

## Project Structure

```
.
├── README.md                    # Project overview
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── Makefile                     # Build automation
├── deploy.sh                    # Deployment script
├── .env.example                 # Environment template
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System design
│   ├── SETUP.md                 # Installation guide
│   ├── EXAMPLES.md              # Usage examples
│   ├── SECURITY.md              # Security practices
│   └── SCALABILITY.md           # Scaling strategies
│
├── sql/                         # Athena queries
│   ├── feature_engineering/     # Data processing queries
│   ├── sentiment_analysis/      # Sentiment pipeline queries
│   └── headline_rewriter/       # Headline processing queries
│
├── src/                         # Shared code
│   ├── config/                  # Configuration management
│   └── utils/                   # Utility functions
│
├── pipelines/                   # ML pipelines
│   ├── sentiment_analysis/      # FinBERT pipeline
│   ├── headline_rewriter/       # Mistral headline generation
│   ├── model_training/          # Fine-tuning pipeline
│   └── inference/               # Prediction pipeline
│
├── docker/                      # Container definitions
│   └── Dockerfile               # Base image
│
└── notebooks/                   # Exploratory analysis
    ├── 01_data_collection.ipynb
    ├── 02_feature_engineering.ipynb
    └── 03_model_evaluation.ipynb
```

## Quick Start

### Prerequisites

- AWS Account with SageMaker permissions
- Docker
- Python 3.8+
- Hugging Face API token

### Installation

```bash
git clone https://github.com/raulprocha/llms-gold_market.git
cd llms-gold_market
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

```bash
AWS_REGION=us-east-1
AWS_BUCKET=your-bucket-name
AWS_SAGEMAKER_ROLE=arn:aws:iam::ACCOUNT:role/SageMakerRole
AWS_ECR_IMAGE=ACCOUNT.dkr.ecr.REGION.amazonaws.com/IMAGE:TAG
HF_API_TOKEN=your_huggingface_token
```

### Build and Deploy

```bash
# Build Docker image
make build

# Deploy to ECR
make deploy
```

### Run Pipelines

```bash
# Sentiment analysis
python pipelines/sentiment_analysis/run.py

# Model training
python pipelines/model_training/run.py

# Inference
python pipelines/inference/run.py
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Direction F1-Score | 0.90 |
| Direction Accuracy | 0.85 |
| Magnitude F1-Score | 0.37 |
| Magnitude Accuracy | 0.77 |
| JSON Validity | 100% |
| Processing Speed | ~1000 news/hour |

## Cost Analysis

Typical AWS costs for production workload:

- **Training** (ml.g5.2xlarge): ~$2.50/hour
- **Inference** (ml.g4dn.xlarge): ~$0.70/hour
- **Storage** (S3): ~$0.023/GB/month
- **Total for full pipeline**: ~$120 for complete training cycle

## Data Sources

- **News**: Alpaca Markets API (financial news feed)
- **Market Data**: MetaTrader 5 (XAU/USD 30-min candles)
- **Correlates**: Gold ETFs (GLD, IAU), USD indices, real yields

## Models

### FinBERT Sentiment Analysis
- Model: `yiyanghkust/finbert-tone`
- Task: 3-class sentiment (Positive/Neutral/Negative)
- Confidence scoring for intensity

### Mistral-7B Fine-tuning
- Base: `mistralai/Mistral-7B-Instruct-v0.2`
- Method: LoRA (r=16, alpha=32)
- Precision: 4-bit quantization
- Training: 3 epochs, ~5200 steps

## Technical Highlights

- **Efficient Fine-tuning**: LoRA reduces trainable parameters by 99%
- **GPU Optimization**: Mixed precision training, gradient accumulation
- **Robust Evaluation**: Stratified temporal splits, early stopping
- **Production Ready**: Containerized, versioned, monitored

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Setup Guide](docs/SETUP.md) - Detailed installation instructions
- [Examples](docs/EXAMPLES.md) - Usage examples and code samples
- [Security](docs/SECURITY.md) - Security best practices
- [Scalability](docs/SCALABILITY.md) - Scaling strategies

## Use Cases

1. **Algorithmic Trading**: Generate trading signals from news
2. **Risk Management**: Anticipate volatility from events
3. **Market Research**: Analyze news impact patterns
4. **Portfolio Optimization**: Adjust gold exposure based on sentiment

## License

MIT License

## Contact

**Raul Rocha**  
GitHub: [@raulprocha](https://github.com/raulprocha)  
Email: raulrocha.rpr@gmail.com

---

*Production-grade ML engineering for financial applications using modern LLM techniques and cloud infrastructure.*
