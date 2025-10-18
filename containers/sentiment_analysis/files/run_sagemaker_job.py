from sagemaker.pytorch import PyTorchProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker import Session
from sagemaker.network import NetworkConfig
import boto3, uuid

session = boto3.Session(region_name="us-east-1")
sagemaker_session = Session(boto_session=session)
role = "arn:aws:iam::378441332365:role/service-role/AmazonSageMaker-ExecutionRole-20250613T151598"

bucket = 'financial-llm-project'
job_name = f"sentiment_analysis_pipeline-{uuid.uuid4().hex[:8]}"

image_uri = '378441332365.dkr.ecr.us-east-1.amazonaws.com/llm-rewriter:v1'

processor = PyTorchProcessor(
    #https://github.com/aws/deep-learning-containers/blob/master/available_images.md#huggingface-training-containers
    image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type='ml.g4dn.xlarge', # for tests use ml.t3.medium, for production ml.g4dn.xlarge or ml.g5.2xlarge
    volume_size_in_gb=50,
    base_job_name=job_name,
    sagemaker_session=sagemaker_session,
    framework_version="1.13",
    env={'NUM_ROWS': 'ALL', 'TRANSFORMERS_CACHE': '/opt/ml/processing/cache', 'SM_MODEL_DIR': '1'},
    network_config=NetworkConfig(enable_network_isolation=False)
)

processor.run(
    code = "process.py",  
    source_dir = "./code",      
    inputs=[
        ProcessingInput(
            source=f's3://{bucket}/finbert_pipeline/input/',
            destination='/opt/ml/processing/input/'
        )
    ],
    outputs=[
        ProcessingOutput(
            source='/opt/ml/processing/output/',
            destination=f's3://{bucket}/finbert_pipeline/output/'
        )
    ],
    wait=True,
    logs=True,
    job_name=job_name
)

print("Job finalizado com sucesso!")

