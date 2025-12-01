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
├── src/
│   ├── config/                    # Configuration management
│   ├── data/                      # Data collection and processing
│   ├── models/                    # Model training and inference
│   └── utils/                     # Shared utilities
├── containers/
│   ├── base/                      # Shared Docker image
│   ├── sentiment_analysis/        # FinBERT pipeline
│   ├── headline_rewriter/         # Mistral headline generation
│   └── model_training/            # Fine-tuning pipeline
├── notebooks/                     # Exploratory analysis
├── sql/                          # Athena queries
├── requirements.txt
└── .env.example
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
# Build base Docker image
cd containers/base
docker build -t gold-ml-base:latest .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag gold-ml-base:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/gold-ml-base:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/gold-ml-base:latest
```

### Run Pipelines

```bash
# Sentiment analysis
python containers/sentiment_analysis/run_job.py

# Headline rewriting
python containers/headline_rewriter/run_job.py

# Model training
python containers/model_training/run_training.py
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

## Use Cases

1. **Algorithmic Trading**: Generate trading signals from news
2. **Risk Management**: Anticipate volatility from events
3. **Market Research**: Analyze news impact patterns
4. **Portfolio Optimization**: Adjust gold exposure based on sentiment

## Limitations

- Predictions are probabilistic, not deterministic
- Performance depends on news quality and timeliness
- Market conditions may change model effectiveness
- Requires continuous retraining for drift adaptation

## Future Enhancements

- Real-time streaming inference
- Multi-asset support (silver, platinum)
- Ensemble with technical indicators
- Explainability dashboard

## License

MIT License

## Contact

**Raul Rocha**  
GitHub: [@raulprocha](https://github.com/raulprocha)  
Email: raulrocha.rpr@gmail.com

---

*This project demonstrates production-grade ML engineering for financial applications using modern LLM techniques and cloud infrastructure.*
