# Usage Examples

Practical examples for common workflows.

## Quick Start Example

```bash
# 1. Setup
git clone https://github.com/raulprocha/llms-gold_market.git
cd llms-gold_market
cp .env.example .env
# Edit .env with your credentials

# 2. Install
make install

# 3. Deploy
make deploy

# 4. Run sentiment analysis
make sentiment
```

## Example 1: Batch Sentiment Analysis

### Input Data (CSV)
```csv
id,symbol,name,generated_headline
1,GLD,SPDR Gold Trust,"Fed signals potential rate cuts, gold outlook improves"
2,IAU,iShares Gold Trust,"Dollar weakens on economic data, gold gains momentum"
3,GLD,SPDR Gold Trust,"Inflation concerns drive investors to safe-haven assets"
```

### Upload to S3
```bash
aws s3 cp headlines.csv s3://financial-llm-project/finbert_pipeline/input/
```

### Run Pipeline
```python
# containers/sentiment_analysis/run_job.py
from src.config.settings import Config
from src.utils.sagemaker_utils import create_sagemaker_session, generate_job_name

config = Config.load()
session = create_sagemaker_session(config.aws.region)
job_name = generate_job_name("sentiment-analysis")

# Job runs automatically...
```

### Expected Output (CSV)
```csv
id,symbol,symbol_name,generated_headline,sentiment,confidence,intensity
1,GLD,SPDR Gold Trust,"Fed signals potential rate cuts...",positive,0.92,strong
2,IAU,iShares Gold Trust,"Dollar weakens on economic data...",positive,0.87,strong
3,GLD,SPDR Gold Trust,"Inflation concerns drive investors...",positive,0.78,moderate
```

### Download Results
```bash
aws s3 cp s3://financial-llm-project/finbert_pipeline/output/output_finbert.csv .
```

## Example 2: Model Training

### Prepare Training Data

```python
# Format: headline, sentiment, context, labels for 4 horizons
import pandas as pd

data = {
    'headline': ['Fed cuts rates unexpectedly'],
    'sentiment': ['positive'],
    'sentiment_confidence': [0.95],
    'context': ['DXY: 103.2, GLD: 185.3, TLT: 95.1'],
    'direction_6h': ['up'],
    'magnitude_6h': ['high'],
    'direction_12h': ['up'],
    'magnitude_12h': ['medium-high'],
    # ... 24h, 48h
}

df = pd.DataFrame(data)
df.to_csv('training_data.csv', index=False)
```

### Upload and Train

```bash
# Upload
aws s3 cp training_data.csv s3://financial-llm-project/llm_pipeline/input/

# Train
make train
```

### Monitor Progress

```bash
# View logs
aws logs tail /aws/sagemaker/ProcessingJobs --follow

# Check S3 for checkpoints
aws s3 ls s3://financial-llm-project/llm_pipeline/checkpoints/
```

## Example 3: Real-time Prediction

### Input Format (JSON)

```json
{
  "headline": "Fed Chair Powell signals dovish stance on inflation",
  "sentiment": "positive",
  "sentiment_confidence": 0.89,
  "context": {
    "DXY": 103.5,
    "GLD": 186.2,
    "IAU": 18.1,
    "TLT": 95.8,
    "current_price": 2045.30
  }
}
```

### Prediction Output (JSON)

```json
{
  "6h": {
    "direction": "up",
    "magnitude": "medium-high",
    "confidence": 0.87
  },
  "12h": {
    "direction": "up",
    "magnitude": "high",
    "confidence": 0.82
  },
  "24h": {
    "direction": "up",
    "magnitude": "medium-high",
    "confidence": 0.75
  },
  "48h": {
    "direction": "neutral",
    "magnitude": "low",
    "confidence": 0.68
  }
}
```

### Interpretation

- **6h**: Expect upward movement, moderate-to-strong magnitude (87% confidence)
- **12h**: Strong upward movement expected (82% confidence)
- **24h**: Continued upward trend, moderating (75% confidence)
- **48h**: Movement likely to stabilize (68% confidence)

## Example 4: Custom Configuration

### Development Setup (.env)

```bash
# Use cheaper instances for testing
INSTANCE_TYPE_TRAINING=ml.t3.medium
INSTANCE_TYPE_INFERENCE=ml.t3.medium
NUM_ROWS=100  # Process only 100 rows
BATCH_SIZE=4
```

### Production Setup (.env)

```bash
# Use GPU instances for performance
INSTANCE_TYPE_TRAINING=ml.g5.12xlarge
INSTANCE_TYPE_INFERENCE=ml.g5.2xlarge
NUM_ROWS=ALL
BATCH_SIZE=16
```

## Example 5: Cost Monitoring

### Set Budget Alert

```bash
aws budgets create-budget \
  --account-id 378441332365 \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

### budget.json
```json
{
  "BudgetName": "ML-Pipeline-Monthly",
  "BudgetLimit": {
    "Amount": "200",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

### Check Current Costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://filter.json
```

## Example 6: Automated Pipeline

### Cron Job for Daily Processing

```bash
# crontab -e
0 2 * * * cd /path/to/project && make sentiment >> /var/log/ml-pipeline.log 2>&1
```

### Python Scheduler

```python
import schedule
import time
from containers.sentiment_analysis.run_job import main

def job():
    print("Running daily sentiment analysis...")
    main()

schedule.every().day.at("02:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Example 7: Error Handling

### Check Job Status

```python
import boto3

client = boto3.client('sagemaker', region_name='us-east-1')

response = client.describe_processing_job(
    ProcessingJobName='sentiment-analysis-abc123'
)

status = response['ProcessingJobStatus']
print(f"Job status: {status}")

if status == 'Failed':
    print(f"Failure reason: {response['FailureReason']}")
```

### Retry Failed Job

```python
from src.utils.sagemaker_utils import run_processing_job

try:
    run_processing_job(...)
except Exception as e:
    print(f"Job failed: {e}")
    print("Retrying with smaller batch size...")
    # Adjust config and retry
```

## Example 8: Data Validation

### Validate Input Data

```python
import pandas as pd

def validate_input(df):
    required_cols = ['id', 'symbol', 'name', 'generated_headline']
    
    # Check columns
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Check for nulls
    if df[required_cols].isnull().any().any():
        raise ValueError("Null values found in required columns")
    
    # Check headline length
    if (df['generated_headline'].str.len() > 500).any():
        raise ValueError("Headlines too long (max 500 chars)")
    
    print("✅ Validation passed")

df = pd.read_csv('headlines.csv')
validate_input(df)
```

## Example 9: Performance Benchmarking

### Measure Processing Time

```python
import time
from datetime import datetime

start_time = time.time()
job_name = generate_job_name("benchmark")

run_processing_job(...)

end_time = time.time()
duration = end_time - start_time

print(f"Job completed in {duration:.2f} seconds")
print(f"Processing rate: {num_rows / duration:.2f} rows/second")
```

### Compare Instance Types

```python
results = {
    'ml.t3.medium': {'time': 3600, 'cost': 0.05},
    'ml.g4dn.xlarge': {'time': 600, 'cost': 0.70},
    'ml.g5.2xlarge': {'time': 300, 'cost': 2.50}
}

for instance, metrics in results.items():
    cost_per_row = (metrics['cost'] * metrics['time'] / 3600) / 1000
    print(f"{instance}: ${cost_per_row:.4f} per row")
```

## Example 10: Integration with Trading System

### Webhook Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class NewsEvent(BaseModel):
    headline: str
    timestamp: str

@app.post("/predict")
async def predict(event: NewsEvent):
    # 1. Rewrite headline
    rewritten = rewrite_headline(event.headline)
    
    # 2. Analyze sentiment
    sentiment = analyze_sentiment(rewritten)
    
    # 3. Get prediction
    prediction = model.predict(rewritten, sentiment)
    
    # 4. Generate trading signal
    if prediction['6h']['direction'] == 'up' and prediction['6h']['confidence'] > 0.8:
        return {"action": "BUY", "confidence": prediction['6h']['confidence']}
    
    return {"action": "HOLD", "confidence": 0.0}
```

### Usage

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"headline": "Fed cuts rates", "timestamp": "2025-12-01T10:00:00Z"}'
```

## Tips & Best Practices

### 1. Start Small
- Test with `NUM_ROWS=100` before full dataset
- Use `ml.t3.medium` for development

### 2. Monitor Costs
- Set up budget alerts
- Use spot instances for training
- Delete old checkpoints

### 3. Version Control
- Tag Docker images with version numbers
- Save model artifacts with timestamps
- Document configuration changes

### 4. Error Recovery
- Enable checkpointing for long jobs
- Implement retry logic
- Log all operations

### 5. Performance Optimization
- Batch similar requests
- Cache model outputs
- Use appropriate instance types

---

For more examples, see the [GitHub repository](https://github.com/raulprocha/llms-gold_market).
