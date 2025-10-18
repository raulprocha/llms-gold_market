import os
import uuid
import boto3
from dotenv import load_dotenv
from huggingface_hub import login
from sagemaker import Session
from sagemaker.pytorch import PyTorchProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.network import NetworkConfig

# === Load environment variables ===
load_dotenv()

# Retrieve from .env
hf_token = os.getenv("HF_API_TOKEN")
region = os.getenv("AWS_REGION")
bucket = os.getenv("AWS_BUCKET")
role = os.getenv("AWS_SAGEMAKER_ROLE")
image_uri = os.getenv("AWS_ECR_IMAGE")

# === Login to Hugging Face ===
login(hf_token)

# === AWS session and SageMaker setup ===
session = boto3.Session(region_name=region)
sagemaker_session = Session(boto_session=session)
job_name = f"llm-pipeline-{uuid.uuid4().hex[:8]}"

# === Define processor ===
processor = PyTorchProcessor(
    image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type='ml.g5.2xlarge',  # test: ml.t3.medium | prod: ml.g4dn.xlarge/ml.g5.2xlarge
    volume_size_in_gb=50,
    base_job_name=job_name,
    sagemaker_session=sagemaker_session,
    framework_version="1.13",
    env={
        'NUM_ROWS': 'ALL',
        'TRANSFORMERS_CACHE': '/opt/ml/processing/cache',
        'SM_MODEL_DIR': '/opt/ml/model',
        'CHECKPOINT_DIR': '/opt/ml/checkpoints',
        'HF_TOKEN': hf_token  # passed securely via environment
    },
    network_config=NetworkConfig(enable_network_isolation=False)
)

# === Run processing job ===
processor.run(
    code="run.py",
    source_dir="./code",
    inputs=[
        ProcessingInput(
            source=f's3://{bucket}/llm_pipeline/input/',
            destination='/opt/ml/processing/input/'
        ),
        ProcessingInput(   # resume from last checkpoint if available
            source=f's3://{bucket}/llm_pipeline/checkpoints/',
            destination='/opt/ml/processing/input/checkpoints/',
            input_name="checkpoint"
        )
    ],
    outputs=[
        ProcessingOutput(
            source='/opt/ml/processing/output/',
            destination=f's3://{bucket}/llm_pipeline/output/'
        ),
        ProcessingOutput(   # save checkpoints
            source='/opt/ml/processing/outputs/checkpoints/',
            destination=f's3://{bucket}/llm_pipeline/checkpoints/'
        )
    ],
    wait=True,
    logs=True,
    job_name=job_name
)

print("✅ SageMaker job completed successfully!")
