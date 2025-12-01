# Security Guidelines

## Secrets Management

### Never Commit
- ❌ AWS credentials (access keys, secret keys)
- ❌ Account IDs in code (use environment variables)
- ❌ Hugging Face tokens
- ❌ API keys
- ❌ `.env` files

### Always Use
- ✅ Environment variables (`.env` file locally)
- ✅ AWS Secrets Manager (production)
- ✅ IAM roles (for AWS services)
- ✅ `.env.example` as template (no real values)

## Configuration Files

### Safe to Commit
```bash
.env.example          # Template with placeholders
requirements.txt      # Python dependencies
Dockerfile           # Container definition
*.md                 # Documentation
```

### Never Commit
```bash
.env                 # Real credentials
.aws/                # AWS CLI credentials
*.pem                # SSH keys
*.key                # Private keys
```

## AWS Best Practices

### IAM Roles
Use IAM roles instead of access keys when possible:
```python
# Good: Uses IAM role attached to SageMaker
session = boto3.Session()

# Avoid: Hardcoded credentials
session = boto3.Session(
    aws_access_key_id='AKIAIOSFODNN7EXAMPLE',  # ❌ Never do this
    aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
)
```

### Least Privilege
Grant minimum required permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/*"
    }
  ]
}
```

### Encryption
- Enable S3 bucket encryption (AES-256 or KMS)
- Use HTTPS for all API calls
- Encrypt sensitive data at rest

## Code Review Checklist

Before committing, verify:
- [ ] No hardcoded credentials
- [ ] No account IDs in code
- [ ] `.env` in `.gitignore`
- [ ] All secrets use environment variables
- [ ] No API tokens in logs
- [ ] No sensitive data in error messages

## Scanning for Secrets

### Manual Check
```bash
# Search for potential secrets
grep -r "aws_access_key\|aws_secret\|password\|token" --include="*.py" --include="*.sh"

# Check what will be committed
git diff --cached | grep -i "secret\|password\|token\|key"
```

### Automated Tools
```bash
# Install git-secrets
git clone https://github.com/awslabs/git-secrets
cd git-secrets && make install

# Setup hooks
git secrets --install
git secrets --register-aws

# Scan repository
git secrets --scan
```

## Production Deployment

### Use AWS Secrets Manager
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('prod/ml-pipeline/credentials')
hf_token = secrets['HF_API_TOKEN']
```

### Environment-specific Configs
```bash
# Development
.env.dev

# Staging
.env.staging

# Production (use Secrets Manager instead)
# .env.prod  ❌ Don't create this file
```

## Incident Response

### If Credentials Are Leaked

1. **Immediately rotate credentials**
   ```bash
   # Deactivate old access key
   aws iam update-access-key --access-key-id AKIAIOSFODNN7EXAMPLE --status Inactive
   
   # Create new access key
   aws iam create-access-key --user-name your-username
   ```

2. **Remove from Git history**
   ```bash
   # Use BFG Repo-Cleaner
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

3. **Force push (if repository is private)**
   ```bash
   git push --force
   ```

4. **Notify team and audit logs**

## Monitoring

### CloudTrail
Enable CloudTrail to audit all API calls:
```bash
aws cloudtrail create-trail --name ml-pipeline-audit --s3-bucket-name audit-logs
aws cloudtrail start-logging --name ml-pipeline-audit
```

### GuardDuty
Enable GuardDuty for threat detection:
```bash
aws guardduty create-detector --enable
```

### Cost Alerts
Set up billing alerts to detect unusual activity:
```bash
aws budgets create-budget --account-id <ACCOUNT_ID> --budget file://budget.json
```

## Compliance

### Data Privacy
- Anonymize PII in logs
- Encrypt data in transit and at rest
- Implement data retention policies

### Audit Trail
- Log all model training runs
- Track data access
- Version control all code changes

## Contact

For security issues:
- Email: raulrocha.rpr@gmail.com
- Subject: [SECURITY] Brief description
- Do not disclose publicly until resolved
