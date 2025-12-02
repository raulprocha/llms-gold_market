"""Model evaluation utilities for test set metrics."""

import json
import os
from typing import Dict, Any
from transformers import Trainer
from datasets import Dataset


def run_test_evaluation(
    trainer: Trainer,
    test_dataset: Dataset,
    output_dir: str
) -> Dict[str, Any]:
    """Evaluate model on test set and save metrics.
    
    Runs evaluation on the test dataset using the trained model
    and saves results to JSON file.
    
    Args:
        trainer: Hugging Face Trainer instance with trained model
        test_dataset: Tokenized test dataset
        output_dir: Directory to save evaluation metrics
        
    Returns:
        Dictionary containing test metrics (loss, accuracy, F1, etc.)
        
    Raises:
        IOError: If unable to write metrics file
        
    Example:
        >>> metrics = run_test_evaluation(trainer, test_ds, "./output")
        >>> print(f"Test accuracy: {metrics['test_accuracy']:.3f}")
    """
    metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
    print("📊 Test metrics:", metrics)

    # Save to output_dir/test_metrics.json
    output_path = os.path.join(output_dir, "test_metrics.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Test metrics saved to: {output_path}")
    return metrics
