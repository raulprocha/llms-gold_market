# Setup Guide

Complete guide for setting up the gold market prediction pipeline.

## Prerequisites

### AWS Account Setup

1. **Create AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com
   - Sign up for an account

2. **Create IAM User** (recommended over root)
   ```bash
   # Via AWS Console:
   # IAM → Users → Create User
   # Attach policies: AmazonSageMakerFullAccess, AmazonS3FullAccess, AmazonEC2ContainerRegistryFullAccess
   ```

3. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
   ```

4. **Create SageMaker Execution Role**
   ```bash
   # Via AWS Console:
   # IAM → Roles → Create Role
   # Use case: SageMaker
   # Attach policies: AmazonSageMakerFullAccess, AmazonS3FullAccess
   # Copy the Role ARN
   ```

5. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://your-bucket-name --region us-east-1
   ```

6. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name gold-ml-pipeline --region us-east-1
   ```

### Local Environment

1. **Install Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Install Docker**
   ```bash
   docker --version  # Verify installation
   ```

3. **Install Git**
   ```bash
   git --version
   ```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/raulprocha/llms-gold_market.git
cd llms-gold_market
```

### 2. Create Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
make install
# Or manually:
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_BUCKET=your-bucket-name
AWS_SAGEMAKER_ROLE=arn:aws:iam::<ACCOUNT_ID>:role/SageMakerRole
AWS_ECR_IMAGE=<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/gold-ml-pipeline:latest

# Hugging Face (get token from https://huggingface.co/settings/tokens)
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Instance Types
INSTANCE_TYPE_TRAINING=ml.g5.2xlarge
INSTANCE_TYPE_INFERENCE=ml.g4dn.xlarge

# Processing
NUM_ROWS=ALL
BATCH_SIZE=16
```

**Replace placeholders:**
- `<ACCOUNT_ID>`: Your AWS account ID (12 digits)
- `your-bucket-name`: Your S3 bucket name
- `hf_xxxxxxxxxxxxxxxxxxxxx`: Your Hugging Face token

## Data Preparation

### 1. Upload Training Data to S3

```bash
# Structure your data as:
# s3://your-bucket/llm_pipeline/input/training_data.csv
# s3://your-bucket/finbert_pipeline/input/headlines.csv

aws s3 cp local_data.csv s3://your-bucket/llm_pipeline/input/
```

### 2. Expected Data Format

**For Sentiment Analysis** (`finbert_pipeline/input/`):
```csv
id,symbol,name,generated_headline
1,GLD,SPDR Gold Trust,"Fed signals rate cuts, gold outlook positive"
```

**For Model Training** (`llm_pipeline/input/`):
```csv
headline,sentiment,context,direction_6h,magnitude_6h,...
"Gold rises on Fed dovish stance",positive,"...",up,high,...
```

## Docker Image Deployment

### 1. Build Image

```bash
make build
# Or manually:
cd containers/base
docker build -t gold-ml-pipeline:latest .
```

### 2. Test Locally (optional)

```bash
docker run --rm gold-ml-pipeline:latest --version
```

### 3. Deploy to ECR

```bash
make deploy
# Or manually:
./deploy.sh
```

This will:
- Build the Docker image
- Authenticate with ECR
- Tag the image
- Push to your ECR repository

## Running Pipelines

### 1. Sentiment Analysis

```bash
make sentiment
# Or:
python containers/sentiment_analysis/run_job.py
```

**What it does:**
- Reads headlines from S3
- Applies FinBERT sentiment classification
- Outputs results to S3

**Expected runtime:** ~30 minutes for 1000 headlines on ml.g4dn.xlarge

### 2. Model Training

```bash
make train
# Or:
python containers/mistral_finetuning/run_training.py
```

**What it does:**
- Loads training data from S3
- Fine-tunes Mistral-7B with LoRA
- Saves model checkpoints to S3

**Expected runtime:** ~4 hours on ml.g5.2xlarge (3 epochs, 27K samples)

**Cost estimate:** ~$10 for full training run

## Monitoring

### View SageMaker Jobs

```bash
# List recent jobs
aws sagemaker list-processing-jobs --max-results 10

# Get job details
aws sagemaker describe-processing-job --processing-job-name <job-name>
```

### View Logs

```bash
# Via AWS Console:
# CloudWatch → Log Groups → /aws/sagemaker/ProcessingJobs
```

### Check S3 Outputs

```bash
aws s3 ls s3://your-bucket/llm_pipeline/output/
aws s3 ls s3://your-bucket/finbert_pipeline/output/
```

## Troubleshooting

### Issue: "Unable to locate credentials"
**Solution:** Run `aws configure` and enter your credentials

### Issue: "Access Denied" on S3
**Solution:** Check IAM role has S3 permissions

### Issue: "Image not found" in SageMaker
**Solution:** Verify ECR image URI in `.env` is correct

### Issue: Out of memory during training
**Solution:** 
- Reduce `BATCH_SIZE` in `.env`
- Use larger instance type (ml.g5.12xlarge)

### Issue: Job fails immediately
**Solution:** Check CloudWatch logs for detailed error messages

## Cost Management

### Estimate Costs

Use AWS Pricing Calculator: https://calculator.aws

**Typical costs:**
- ml.g5.2xlarge: $2.50/hour
- ml.g4dn.xlarge: $0.70/hour
- S3 storage: $0.023/GB/month
- Data transfer: Usually free within same region

### Cost Optimization Tips

1. **Use Spot Instances** (up to 70% savings)
   ```python
   # In run_training.py, add:
   use_spot_instances=True,
   max_wait_time_in_seconds=86400
   ```

2. **Stop jobs when not needed**
   ```bash
   aws sagemaker stop-processing-job --processing-job-name <job-name>
   ```

3. **Set S3 lifecycle policies**
   ```bash
   # Delete old checkpoints after 30 days
   aws s3api put-bucket-lifecycle-configuration --bucket your-bucket --lifecycle-configuration file://lifecycle.json
   ```

4. **Use smaller instances for testing**
   - Development: ml.t3.medium ($0.05/hour)
   - Testing: ml.m5.xlarge ($0.23/hour)

## Scalability Considerations

### Horizontal Scaling

**Multi-instance Training**
```python
# In run_training.py
processor = create_processor(
    instance_count=4,  # Use 4 instances
    ...
)
```

**Distributed Data Processing**
```python
# Use SageMaker Processing with multiple instances
# Data automatically partitioned across instances
```

### Vertical Scaling

**Instance Type Selection**
```bash
# Development
INSTANCE_TYPE_TRAINING=ml.t3.medium

# Small-scale production
INSTANCE_TYPE_TRAINING=ml.g4dn.xlarge

# Large-scale production
INSTANCE_TYPE_TRAINING=ml.g5.12xlarge  # 4 GPUs, 48 vCPUs, 192GB RAM
```

### Auto-scaling for Real-time Endpoints

```python
from sagemaker.predictor import Predictor

predictor = Predictor(endpoint_name='gold-prediction')

# Configure auto-scaling
predictor.update_endpoint(
    initial_instance_count=1,
    instance_type='ml.g4dn.xlarge',
    auto_scaling_config={
        'min_capacity': 1,
        'max_capacity': 10,
        'target_value': 70.0,  # Target CPU utilization
        'scale_in_cooldown': 300,
        'scale_out_cooldown': 60
    }
)
```

### Data Partitioning

```bash
# Partition S3 data by date for efficient querying
s3://bucket/data/year=2025/month=12/day=01/
```

### Batch Processing Optimization

```python
# Process in batches to optimize throughput
BATCH_SIZE=32  # Larger batches = better GPU utilization
NUM_WORKERS=4  # Parallel data loading
```

## Next Steps

1. **Run a test job** with small dataset
2. **Monitor costs** in AWS Cost Explorer
3. **Scale up** to full dataset
4. **Set up CI/CD** for automated deployments
5. **Deploy inference endpoint** for real-time predictions

## Support

For issues or questions:
- GitHub Issues: https://github.com/raulprocha/llms-gold_market/issues
- Email: raulrocha.rpr@gmail.com
