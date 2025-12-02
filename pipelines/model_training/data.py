"""Dataset loading and preprocessing for model training."""

from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from src.prompts import build_prompt, build_target_json


def load_dataset(csv_path: str) -> Tuple[Dataset, Dataset, Dataset]:
    """Load and split dataset for training, validation, and testing.
    
    Reads CSV file, builds prompt and target columns, and splits data
    into train/validation/test sets with stratified sampling.
    
    Args:
        csv_path: Path to CSV file containing training data
        
    Returns:
        Tuple of (test_dataset, train_dataset, validation_dataset)
        Each dataset is a Hugging Face Dataset object
        
    Note:
        Currently limited to first 100 rows for testing.
        Remove df.head(100) for full dataset processing.
        
    Example:
        >>> test_ds, train_ds, val_ds = load_dataset("data/training.csv")
        >>> print(f"Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")
    """
    df = pd.read_csv(csv_path)
    df = df.head(100)  # TODO: Remove for production
    
    # Build prompt and target_json columns
    df["prompt"] = df.apply(build_prompt, axis=1)
    df["target_json"] = df.apply(build_target_json, axis=1)

    # Split: 95% train+val, 5% test
    train_val_df, test_df = train_test_split(
        df, test_size=0.05, random_state=42
    )
    
    # Split train+val: ~90% train, ~5% val
    train_df, val_df = train_test_split(
        train_val_df, test_size=0.05/0.95, random_state=42
    )

    test_ds = Dataset.from_pandas(test_df)
    train_ds = Dataset.from_pandas(train_df)
    val_ds = Dataset.from_pandas(val_df)

    return test_ds, train_ds, val_ds
