# src/evaluate.py
from src.tokenizer import tokenize_batch
import json, os

def run_test_evaluation(trainer, test_tok, output_dir):
    metrics = trainer.evaluate(test_tok, metric_key_prefix="test")
    print("📊 Test metrics:", metrics)

    # salva em output_dir/test_metrics.json
    output_path = os.path.join(output_dir, "test_metrics.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Test metrics saved to: {output_path}")
    return metrics
