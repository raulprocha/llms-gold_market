"""
Legacy script - Use containers/mistral_finetuning/run_training.py instead.
This file is kept for backward compatibility.
"""

import os
import sys

# Redirect to new implementation
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

print("⚠️  This script is deprecated. Use: python containers/mistral_finetuning/run_training.py")
print("Redirecting to new implementation...\n")

from containers.mistral_finetuning.run_training import main

if __name__ == "__main__":
    main()
