"""
SageMaker job runner for FinBERT sentiment analysis pipeline.
Processes financial headlines and generates sentiment classifications.
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
    job_name = generate_job_name("sentiment-analysis")
    
    # Create processor
    processor = create_processor(
        image_uri=config.aws.ecr_image,
        role=config.aws.sagemaker_role,
        instance_type=config.model.instance_type_inference,
        instance_count=1,
        volume_size_gb=50,
        job_name=job_name,
        sagemaker_session=session,
        env_vars={'NUM_ROWS': config.model.num_rows}
    )
    
    # Define I/O
    inputs = [
        ProcessingInput(
            source=f's3://{config.aws.bucket}/finbert_pipeline/input/',
            destination='/opt/ml/processing/input/'
        )
    ]
    
    outputs = [
        ProcessingOutput(
            source='/opt/ml/processing/output/',
            destination=f's3://{config.aws.bucket}/finbert_pipeline/output/'
        )
    ]
    
    # Run job
    print(f"🚀 Starting sentiment analysis job: {job_name}")
    run_processing_job(
        processor=processor,
        code_file="process.py",
        source_dir="./files/code",
        inputs=inputs,
        outputs=outputs,
        job_name=job_name
    )


if __name__ == "__main__":
    main()
