"""
Legacy script - Use containers/sentiment_analysis/run_job.py instead.
This file is kept for backward compatibility.
"""

import os
import sys

# Redirect to new implementation
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

print("⚠️  This script is deprecated. Use: python containers/sentiment_analysis/run_job.py")
print("Redirecting to new implementation...\n")

from containers.sentiment_analysis.run_job import main

if __name__ == "__main__":
    main()
