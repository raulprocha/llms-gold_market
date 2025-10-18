# run.py
import os, yaml
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "bitsandbytes==0.43.3", "scikit-learn==1.3.2", "hf_xet"])
from src.utils import is_sagemaker, set_seed_and_paths
from src.model import load_model_tokenizer
from src.data import load_dataset
from src.tokenizer import tokenize_batch
from src.train import make_trainer
from src.evaluate import run_test_evaluation
from transformers.trainer_utils import get_last_checkpoint


if __name__ == "__main__":
    cfg = yaml.safe_load(open("config/config.yaml"))
    sm = is_sagemaker()
    paths = cfg["paths"]
    input_csv = paths["input_csv_sagemaker"] if sm else paths["input_csv_local"]
    output_dir = paths["output_dir_sagemaker"] if sm else paths["output_dir_local"]
    cache_dir = paths["cache_sagemaker"] if sm else paths["cache_local"]

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    set_seed_and_paths(cfg["train"]["seed"])

    model, tokenizer = load_model_tokenizer(cfg, cache_dir)
    test_ds, train_ds, val_ds = load_dataset(input_csv)

    # map batched com tokenize_batch
    def _tok(batch):
        out = tokenize_batch(batch, tokenizer, cfg["tokenization"]["max_input_length"])
        return {k: v.tolist() if hasattr(v, "tolist") else v for k, v in out.items()}

    remove_cols = train_ds.column_names

    train_tok = train_ds.map(_tok, batched=True, remove_columns=train_ds.column_names)
    val_tok   = val_ds.map(_tok,   batched=True, remove_columns=val_ds.column_names)
    test_tok = test_ds.map(_tok, batched=True, remove_columns=test_ds.column_names)

    trainer = make_trainer(model, tokenizer, train_tok, val_tok, cfg, output_dir)
    ckpt = get_last_checkpoint(output_dir)

    trainer.train(resume_from_checkpoint=ckpt if ckpt else None)
    trainer.save_model(output_dir)
    
    tokenizer.save_pretrained(output_dir)

    run_test_evaluation(trainer, test_tok, output_dir)
