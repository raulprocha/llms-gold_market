# Scalability Guide

## Overview

This system is designed to scale from prototype (1K headlines/day) to enterprise (1M+ headlines/day).

## Scaling Dimensions

### 1. Data Volume Scaling

#### Current: ~30K headlines
```python
# Single instance processing
INSTANCE_TYPE = "ml.g4dn.xlarge"
INSTANCE_COUNT = 1
BATCH_SIZE = 16
```

#### Medium: ~300K headlines
```python
# Multi-instance processing
INSTANCE_TYPE = "ml.g4dn.xlarge"
INSTANCE_COUNT = 10
BATCH_SIZE = 32
```

#### Large: ~3M headlines
```python
# Distributed processing with larger instances
INSTANCE_TYPE = "ml.g5.12xlarge"
INSTANCE_COUNT = 20
BATCH_SIZE = 64
```

### 2. Throughput Scaling

#### Batch Processing (Current)
- **Throughput**: 1,000 headlines/hour
- **Latency**: Minutes
- **Cost**: ~$0.70/hour
- **Use case**: Daily analysis, backtesting

#### Real-time Endpoint
- **Throughput**: 100 requests/second
- **Latency**: <100ms
- **Cost**: ~$500/month (24/7)
- **Use case**: Live trading, immediate response

#### Hybrid (Recommended)
- **Batch**: Bulk processing overnight
- **Real-time**: Critical news during market hours
- **Cost**: ~$200/month
- **Use case**: Most production scenarios

## Implementation Strategies

### Horizontal Scaling

#### Multi-instance Processing
```python
from src.utils.sagemaker_utils import create_processor

processor = create_processor(
    instance_count=10,  # Scale out
    instance_type="ml.g4dn.xlarge",
    ...
)
```

**Benefits:**
- Linear throughput increase
- Fault tolerance (one instance fails, others continue)
- Cost-effective for large batches

**Considerations:**
- Data must be partitionable
- Slight overhead for coordination
- S3 read/write becomes bottleneck at scale

#### Data Partitioning
```python
# Partition by date
s3://bucket/input/year=2025/month=12/day=01/part-0001.csv
s3://bucket/input/year=2025/month=12/day=01/part-0002.csv

# Partition by symbol
s3://bucket/input/symbol=GLD/data.csv
s3://bucket/input/symbol=IAU/data.csv
```

### Vertical Scaling

#### Instance Type Progression
```python
# Development: CPU only
ml.t3.medium      # $0.05/hour, 2 vCPU, 4GB RAM

# Small production: Single GPU
ml.g4dn.xlarge    # $0.70/hour, 1 GPU, 4 vCPU, 16GB RAM

# Medium production: Larger GPU
ml.g5.2xlarge     # $2.50/hour, 1 A10G GPU, 8 vCPU, 32GB RAM

# Large production: Multi-GPU
ml.g5.12xlarge    # $10/hour, 4 A10G GPUs, 48 vCPU, 192GB RAM
```

**When to scale up:**
- Batch size limited by memory
- GPU utilization < 50%
- Training time too long

### Auto-scaling

#### SageMaker Endpoint Auto-scaling
```python
import boto3

client = boto3.client('application-autoscaling')

# Register scalable target
client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/gold-prediction/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=10
)

# Create scaling policy
client.put_scaling_policy(
    PolicyName='gold-prediction-scaling',
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/gold-prediction/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% invocations per instance
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,
        'ScaleOutCooldown': 60
    }
)
```

## Performance Optimization

### GPU Utilization

#### Monitor GPU Usage
```python
import torch

print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

#### Optimize Batch Size
```python
# Find optimal batch size
for batch_size in [8, 16, 32, 64]:
    try:
        # Test with sample data
        process_batch(data, batch_size)
        print(f"✅ Batch size {batch_size} works")
    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"❌ Batch size {batch_size} too large")
            break
```

### Data Loading

#### Parallel Data Loading
```python
from torch.utils.data import DataLoader

dataloader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,  # Parallel loading
    pin_memory=True,  # Faster GPU transfer
    prefetch_factor=2  # Prefetch batches
)
```

#### S3 Optimization
```python
# Use S3 Transfer Acceleration
s3_client = boto3.client(
    's3',
    config=boto3.session.Config(
        s3={'use_accelerate_endpoint': True}
    )
)

# Multipart upload for large files
s3_client.upload_file(
    'large_file.csv',
    'bucket',
    'key',
    Config=boto3.s3.transfer.TransferConfig(
        multipart_threshold=1024 * 25,  # 25MB
        max_concurrency=10
    )
)
```

### Model Optimization

#### Quantization
```python
# 4-bit quantization (already implemented)
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    quantization_config=bnb_config
)
```

#### Mixed Precision Training
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    with autocast():
        outputs = model(**batch)
        loss = outputs.loss
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## Cost vs Performance Trade-offs

### Scenario Analysis

#### Scenario 1: Daily Batch (10K headlines)
```
Option A: Single ml.g4dn.xlarge
- Time: 10 hours
- Cost: $7.00
- Throughput: 1K/hour

Option B: 10x ml.g4dn.xlarge
- Time: 1 hour
- Cost: $7.00
- Throughput: 10K/hour

Recommendation: Option B (same cost, 10x faster)
```

#### Scenario 2: Real-time (100 req/sec)
```
Option A: ml.g4dn.xlarge (no auto-scaling)
- Capacity: 50 req/sec
- Cost: $500/month
- Risk: Overload during peaks

Option B: ml.g4dn.xlarge (auto-scaling 1-5)
- Capacity: 50-250 req/sec
- Cost: $500-2500/month (avg $800)
- Risk: Low

Recommendation: Option B (handles peaks)
```

## Monitoring at Scale

### Key Metrics

#### System Metrics
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Put custom metrics
cloudwatch.put_metric_data(
    Namespace='MLPipeline',
    MetricData=[
        {
            'MetricName': 'ProcessingRate',
            'Value': headlines_per_second,
            'Unit': 'Count/Second'
        },
        {
            'MetricName': 'GPUUtilization',
            'Value': gpu_usage_percent,
            'Unit': 'Percent'
        }
    ]
)
```

#### Business Metrics
- Predictions per day
- Average latency
- Error rate
- Cost per prediction

### Alerting
```python
# Create CloudWatch alarm
cloudwatch.put_metric_alarm(
    AlarmName='HighLatency',
    MetricName='ModelLatency',
    Namespace='MLPipeline',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=1000,  # 1 second
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:alerts']
)
```

## Database Scaling

### Athena Optimization

#### Partitioning
```sql
-- Partition by date for efficient queries
CREATE EXTERNAL TABLE news_partitioned (
    id STRING,
    headline STRING,
    sentiment STRING
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET
LOCATION 's3://bucket/news/';
```

#### Compression
```python
# Use Parquet with Snappy compression
df.to_parquet(
    's3://bucket/data.parquet',
    compression='snappy',
    partition_cols=['year', 'month', 'day']
)
```

## Future Scaling Paths

### Phase 1: Current (1K-10K headlines/day)
- Single instance batch processing
- Manual deployment
- Basic monitoring

### Phase 2: Growth (10K-100K headlines/day)
- Multi-instance processing
- Automated deployment (CI/CD)
- Advanced monitoring (Grafana)
- Cost optimization (spot instances)

### Phase 3: Enterprise (100K-1M headlines/day)
- Real-time endpoints with auto-scaling
- Multi-region deployment
- Advanced caching (Redis)
- Custom hardware (Inferentia)

### Phase 4: Hyperscale (1M+ headlines/day)
- Distributed training (SageMaker Training Jobs)
- Model serving on Kubernetes (EKS)
- Edge deployment (IoT/Lambda)
- Custom ASICs

## Best Practices

1. **Start small, scale gradually**
   - Validate with small dataset
   - Measure before scaling
   - Scale one dimension at a time

2. **Monitor everything**
   - System metrics (CPU, GPU, memory)
   - Business metrics (throughput, latency)
   - Cost metrics (per prediction, per hour)

3. **Automate scaling decisions**
   - Use auto-scaling policies
   - Set up alerts for anomalies
   - Implement circuit breakers

4. **Optimize for cost**
   - Use spot instances (70% savings)
   - Right-size instances
   - Implement caching
   - Batch similar requests

5. **Plan for failures**
   - Implement retries
   - Use checkpointing
   - Design for idempotency
   - Have rollback procedures

## Benchmarking

### Load Testing
```python
import concurrent.futures
import time

def load_test(num_requests, concurrency):
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(predict, headline) for headline in headlines[:num_requests]]
        results = [f.result() for f in futures]
    
    duration = time.time() - start
    throughput = num_requests / duration
    
    print(f"Throughput: {throughput:.2f} req/sec")
    print(f"Latency: {duration/num_requests*1000:.2f} ms")

# Test different loads
load_test(100, 10)   # 100 requests, 10 concurrent
load_test(1000, 50)  # 1000 requests, 50 concurrent
```

## Contact

For scalability questions:
- Email: raulrocha.rpr@gmail.com
- GitHub Issues: https://github.com/raulprocha/llms-gold_market/issues
