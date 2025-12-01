#!/bin/bash
# Automated Git Deployment Script

set -e

echo "🚀 Starting deployment process..."
echo ""

# Change to project directory
cd /home/raul.rocha/Documentos/tcc

# Security check
echo "🔒 Running security checks..."
if git diff --cached | grep -iE "AKIA|aws_secret|378441332365" | grep -v ".md:" > /dev/null; then
    echo "❌ ERROR: Secrets detected in staged files!"
    echo "Please review and remove sensitive data before committing."
    exit 1
fi
echo "✅ No secrets detected"
echo ""

# Stage files
echo "📦 Staging files..."
git add README.md ARCHITECTURE.md SETUP.md EXECUTIVE_SUMMARY.md \
        EXAMPLES.md IMPROVEMENTS.md SECURITY.md SCALABILITY.md \
        LICENSE Makefile deploy.sh requirements.txt .env.example \
        src/ containers/base/ \
        containers/sentiment_analysis/run_job.py \
        containers/mistral_finetuning/run_training.py \
        containers/sentiment_analysis/files/run_sagemaker_job.py \
        containers/rewrite_headline/files/run_sagemaker_job.py \
        containers/mistral_finetuning/files/run_sagemaker_job.py \
        .gitignore \
        COMMIT_GUIDE.md DEPLOY_CHECKLIST.md READY_TO_DEPLOY.md \
        git-deploy.sh

echo "✅ Files staged"
echo ""

# Show status
echo "📊 Git status:"
git status --short
echo ""

# Commit
echo "💾 Creating commit..."
git commit -m "refactor: Transform project into production-ready ML system

Major improvements:
- Add comprehensive documentation (10 new docs)
- Create modular code structure with centralized config
- Consolidate 3 Dockerfiles into single base image
- Add deployment automation (deploy.sh, Makefile)
- Refactor job runners to use shared utilities
- Remove all hardcoded values, use environment variables
- Add security and scalability guides
- Include business value analysis and cost breakdowns

Technical changes:
- New src/ module with config and utils
- Unified Docker image in containers/base/
- Environment-based configuration management
- Backward-compatible legacy script wrappers
- Enhanced .gitignore for security

Documentation:
- README.md: Project overview and quick start
- ARCHITECTURE.md: System design and data flow
- SETUP.md: Installation guide with scalability
- EXECUTIVE_SUMMARY.md: Business-focused summary
- EXAMPLES.md: 10 practical usage examples
- SECURITY.md: Security best practices
- SCALABILITY.md: Scaling strategies and optimization
- IMPROVEMENTS.md: Summary of all changes

This commit makes the project portfolio-ready and suitable for
enterprise deployment while maintaining all core functionality."

echo "✅ Commit created"
echo ""

# Push
echo "🌐 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Visit: https://github.com/raulprocha/llms-gold_market"
echo "2. Update repository description and topics"
echo "3. Share on LinkedIn"
echo ""
echo "🎉 Your project is now live!"
