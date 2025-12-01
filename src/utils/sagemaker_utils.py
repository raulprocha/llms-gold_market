"""
Utilities for AWS SageMaker job management.
Provides reusable functions for creating and running SageMaker jobs.
"""

import uuid
import boto3
from typing import Dict, List, Optional
from sagemaker import Session
from sagemaker.pytorch import PyTorchProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.network import NetworkConfig


def create_sagemaker_session(region: str) -> Session:
    """Create a SageMaker session."""
    boto_session = boto3.Session(region_name=region)
    return Session(boto_session=boto_session)


def generate_job_name(prefix: str) -> str:
    """Generate unique job name with prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_processor(
    image_uri: str,
    role: str,
    instance_type: str,
    instance_count: int,
    volume_size_gb: int,
    job_name: str,
    sagemaker_session: Session,
    env_vars: Optional[Dict[str, str]] = None
) -> PyTorchProcessor:
    """
    Create a PyTorch processor for SageMaker.
    
    Args:
        image_uri: ECR image URI
        role: SageMaker execution role ARN
        instance_type: EC2 instance type (e.g., ml.g5.2xlarge)
        instance_count: Number of instances
        volume_size_gb: EBS volume size in GB
        job_name: Base job name
        sagemaker_session: SageMaker session
        env_vars: Optional environment variables
    
    Returns:
        Configured PyTorchProcessor
    """
    default_env = {
        'TRANSFORMERS_CACHE': '/opt/ml/processing/cache',
        'SM_MODEL_DIR': '/opt/ml/model'
    }
    
    if env_vars:
        default_env.update(env_vars)
    
    return PyTorchProcessor(
        image_uri=image_uri,
        role=role,
        instance_count=instance_count,
        instance_type=instance_type,
        volume_size_in_gb=volume_size_gb,
        base_job_name=job_name,
        sagemaker_session=sagemaker_session,
        framework_version="1.13",
        env=default_env,
        network_config=NetworkConfig(enable_network_isolation=False)
    )


def run_processing_job(
    processor: PyTorchProcessor,
    code_file: str,
    source_dir: str,
    inputs: List[ProcessingInput],
    outputs: List[ProcessingOutput],
    job_name: str,
    wait: bool = True
) -> None:
    """
    Run a SageMaker processing job.
    
    Args:
        processor: Configured processor
        code_file: Entry point script name
        source_dir: Directory containing code
        inputs: List of processing inputs
        outputs: List of processing outputs
        job_name: Job name
        wait: Whether to wait for completion
    """
    processor.run(
        code=code_file,
        source_dir=source_dir,
        inputs=inputs,
        outputs=outputs,
        wait=wait,
        logs=True,
        job_name=job_name
    )
    
    if wait:
        print(f"✅ Job {job_name} completed successfully!")
