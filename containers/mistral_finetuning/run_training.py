"""
SageMaker job runner for Mistral-7B fine-tuning pipeline.
Trains the model to predict gold market movements from news.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from sagemaker.processing import ProcessingInput, ProcessingOutput
from src.config.settings import Config
from src.utils.sagemaker_utils import (
    create_sagemaker_session,
    generate_job_name,
    create_processor,
    run_processing_job
)


def main():
    # Load configuration
    config = Config.load()
    config.validate()
    
    # Setup SageMaker
    session = create_sagemaker_session(config.aws.region)
    job_name = generate_job_name("mistral-finetuning")
    
    # Create processor with training-optimized instance
    processor = create_processor(
        image_uri=config.aws.ecr_image,
        role=config.aws.sagemaker_role,
        instance_type=config.model.instance_type_training,
        instance_count=1,
        volume_size_gb=100,
        job_name=job_name,
        sagemaker_session=session,
        env_vars={
            'NUM_ROWS': config.model.num_rows,
            'HF_TOKEN': config.model.hf_token,
            'CHECKPOINT_DIR': '/opt/ml/checkpoints'
        }
    )
    
    # Define I/O with checkpoint support
    inputs = [
        ProcessingInput(
            source=f's3://{config.aws.bucket}/llm_pipeline/input/',
            destination='/opt/ml/processing/input/'
        ),
        ProcessingInput(
            source=f's3://{config.aws.bucket}/llm_pipeline/checkpoints/',
            destination='/opt/ml/processing/input/checkpoints/',
            input_name="checkpoint"
        )
    ]
    
    outputs = [
        ProcessingOutput(
            source='/opt/ml/processing/output/',
            destination=f's3://{config.aws.bucket}/llm_pipeline/output/'
        ),
        ProcessingOutput(
            source='/opt/ml/processing/outputs/checkpoints/',
            destination=f's3://{config.aws.bucket}/llm_pipeline/checkpoints/'
        )
    ]
    
    # Run training job
    print(f"🚀 Starting Mistral fine-tuning job: {job_name}")
    print(f"📊 Instance: {config.model.instance_type_training}")
    run_processing_job(
        processor=processor,
        code_file="run.py",
        source_dir="./files/code",
        inputs=inputs,
        outputs=outputs,
        job_name=job_name
    )


if __name__ == "__main__":
    main()
