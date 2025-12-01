"""
Centralized configuration management for the ML pipeline.
Loads environment variables and provides typed configuration objects.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AWSConfig:
    """AWS service configuration."""
    region: str
    bucket: str
    sagemaker_role: str
    ecr_image: str
    
    @classmethod
    def from_env(cls) -> "AWSConfig":
        return cls(
            region=os.getenv("AWS_REGION", "us-east-1"),
            bucket=os.getenv("AWS_BUCKET"),
            sagemaker_role=os.getenv("AWS_SAGEMAKER_ROLE"),
            ecr_image=os.getenv("AWS_ECR_IMAGE")
        )


@dataclass
class ModelConfig:
    """Model and training configuration."""
    hf_token: str
    instance_type_training: str
    instance_type_inference: str
    batch_size: int
    num_rows: str
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        return cls(
            hf_token=os.getenv("HF_API_TOKEN"),
            instance_type_training=os.getenv("INSTANCE_TYPE_TRAINING", "ml.g5.2xlarge"),
            instance_type_inference=os.getenv("INSTANCE_TYPE_INFERENCE", "ml.g4dn.xlarge"),
            batch_size=int(os.getenv("BATCH_SIZE", "16")),
            num_rows=os.getenv("NUM_ROWS", "ALL")
        )


@dataclass
class Config:
    """Main configuration object."""
    aws: AWSConfig
    model: ModelConfig
    
    @classmethod
    def load(cls) -> "Config":
        return cls(
            aws=AWSConfig.from_env(),
            model=ModelConfig.from_env()
        )
    
    def validate(self) -> None:
        """Validate required configuration values."""
        required = [
            (self.aws.bucket, "AWS_BUCKET"),
            (self.aws.sagemaker_role, "AWS_SAGEMAKER_ROLE"),
            (self.aws.ecr_image, "AWS_ECR_IMAGE"),
            (self.model.hf_token, "HF_API_TOKEN")
        ]
        
        missing = [name for value, name in required if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
