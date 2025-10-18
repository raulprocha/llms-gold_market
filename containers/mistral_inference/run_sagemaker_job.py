import os
import uuid
import boto3
from dotenv import load_dotenv
from sagemaker import Session
from sagemaker.pytorch import PyTorchProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.network import NetworkConfig

# Load environment variables
load_dotenv()

# === Load from .env ===
region = os.getenv("AWS_REGION")
bucket = os.getenv("AWS_BUCKET")
role = os.getenv("AWS_SAGEMAKER_ROLE")
image_uri = os.getenv("AWS_ECR_IMAGE")

# Create session
session = boto3.Session(region_name=region)
sagemaker_session = Session(boto_session=session)

job_name = f"llm-pipeline-{uuid.uuid4().hex[:8]}"

processor = PyTorchProcessor(
    image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type='ml.g4dn.xlarge', 
    volume_size_in_gb=50,
    base_job_name=job_name,
    sagemaker_session=sagemaker_session,
    framework_version="1.13",
    env={
        'NUM_ROWS': '3',
        'TRANSFORMERS_CACHE': '/opt/ml/processing/cache',
        'SM_MODEL_DIR': '1'
    },
    network_config=NetworkConfig(enable_network_isolation=False)
)

processor.run(
    code="process.py",
    source_dir="./code",
    inputs=[
        ProcessingInput(
            source=f's3://{bucket}/llm_pipeline/input/',
            destination='/opt/ml/processing/input/'
        )
    ],
    outputs=[
        ProcessingOutput(
            source='/opt/ml/processing/output/',
            destination=f's3://{bucket}/llm_pipeline/output/'
        )
    ],
    wait=True,
    logs=True,
    job_name=job_name
)

print("✅ SageMaker job completed successfully!")
