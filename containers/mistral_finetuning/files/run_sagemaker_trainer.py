import os
import uuid
import boto3
import yaml
from dotenv import load_dotenv
from huggingface_hub import login
from sagemaker import Session
from sagemaker.inputs import TrainingInput
from sagemaker.huggingface import HuggingFace

# === Load environment variables ===
load_dotenv()

region = os.getenv("AWS_REGION")
bucket = os.getenv("AWS_BUCKET")
role = os.getenv("AWS_SAGEMAKER_ROLE")
hf_token = os.getenv("HF_API_TOKEN")

# === AWS + SageMaker setup ===
session = boto3.Session(region_name=region)
sagemaker_session = Session(boto_session=session)
job_name = f"llm-hftrain-{uuid.uuid4().hex[:8]}"

# === Hugging Face login ===
login(hf_token)

# === Load config.yaml ===
with open("code/config/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)
paths = cfg["paths"]

# === Define training input channel ===
train_input = TrainingInput(
    s3_data=f"s3://{bucket}/llm_pipeline/input/",
    input_mode="File"
)

# === Create Hugging Face Estimator ===
estimator = HuggingFace(
    entry_point="run.py",
    source_dir="code",
    base_job_name="llm-train",
    role=role,
    instance_count=1,
    instance_type="ml.g5.2xlarge",  # test: ml.t3.medium | prod: ml.g4dn.xlarge/ml.g5.2xlarge
    volume_size=50,
    transformers_version="4.36.0",
    pytorch_version="2.1.0",
    py_version="py310",
    sagemaker_session=sagemaker_session,
    max_run=172800,   # 48h
    use_spot_instances=True,
    max_wait=259200,  # 72h (buffer)
    checkpoint_s3_uri=f"s3://{bucket}/llm_pipeline/checkpoints/",
    checkpoint_local_path="/opt/ml/checkpoints",
    environment={
        "HF_TOKEN": hf_token,
        "INPUT_CSV": paths["input_csv_sagemaker"],
        "SM_MODEL_DIR": paths["output_dir_sagemaker"],
        "HF_HOME": paths["cache_sagemaker"],
        "CHECKPOINT_DIR": paths["checkpoint_dir"]
    }
)

# === Launch Training Job ===
estimator.fit({"training": train_input}, job_name=job_name, wait=True)

print("✅ Training job submitted successfully to SageMaker.")
