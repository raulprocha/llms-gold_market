"""
Legacy script - Use containers/rewrite_headline/run_job.py instead.
This file is kept for backward compatibility.
"""

import os
import sys

# Redirect to new implementation
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

print("⚠️  This script is deprecated. Use: python containers/rewrite_headline/run_job.py")
print("Redirecting to new implementation...\n")

# For now, show migration message
print("Please create run_job.py following the pattern in containers/sentiment_analysis/run_job.py")
print("Or use the legacy implementation with environment variables.")

from dotenv import load_dotenv
load_dotenv()

# Use environment variables instead of hardcoded values
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET = os.getenv("AWS_BUCKET")
AWS_SAGEMAKER_ROLE = os.getenv("AWS_SAGEMAKER_ROLE")
AWS_ECR_IMAGE = os.getenv("AWS_ECR_IMAGE")

if not all([AWS_BUCKET, AWS_SAGEMAKER_ROLE, AWS_ECR_IMAGE]):
    raise ValueError("Missing required environment variables. Check your .env file.")

print(f"✅ Configuration loaded from environment")
