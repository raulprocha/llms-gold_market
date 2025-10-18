# src/utils.py
import os, random, numpy as np, torch

def is_sagemaker():
    return "SM_MODEL_DIR" in os.environ or "SM_RESOURCE_CONFIG" in os.environ

def set_seed_and_paths(seed=42):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); 
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

