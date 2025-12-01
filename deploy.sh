#!/bin/bash
# Automated deployment script for Docker image to AWS ECR

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found. Copy .env.example and configure it."
    exit 1
fi

# Validate required variables
if [ -z "$AWS_REGION" ] || [ -z "$AWS_ECR_IMAGE" ]; then
    echo "❌ Missing required environment variables"
    exit 1
fi

# Extract account ID and image name from ECR URI
ACCOUNT_ID=$(echo $AWS_ECR_IMAGE | cut -d'.' -f1)
IMAGE_NAME=$(echo $AWS_ECR_IMAGE | cut -d'/' -f2 | cut -d':' -f1)
IMAGE_TAG=$(echo $AWS_ECR_IMAGE | cut -d':' -f2)

echo "🔧 Building Docker image..."
cd containers/base
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo "🏷️  Tagging image..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${AWS_ECR_IMAGE}

echo "📤 Pushing to ECR..."
docker push ${AWS_ECR_IMAGE}

echo "✅ Deployment complete!"
echo "📦 Image: ${AWS_ECR_IMAGE}"
