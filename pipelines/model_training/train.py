# src/train.py (drop-in)
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

import json, numpy as np
from sklearn.metrics import accuracy_score, f1_score
from transformers import TrainingArguments, Trainer, EarlyStoppingCallback

DIR_FIELDS = ["direction_6h","direction_12h","direction_24h","direction_48h"]
MAG_FIELDS = ["magnitude_6h","magnitude_12h","magnitude_24h","magnitude_48h"]

def _preprocess_logits_for_metrics(logits, labels):
    # alguns modelos retornam tuple
    if isinstance(logits, tuple):
        logits = logits[0]
    # devolve diretamente os token IDs (reduz de float32 [B, T, V] para int64 [B, T])
    return logits.argmax(dim=-1)


def make_compute_metrics(tokenizer):
    pad_id = tokenizer.pad_token_id or 0

    def safe_json(s):
        try:
            return json.loads(s)
        except:
            return {}

    def compute_metrics(eval_pred):
        preds, labels = eval_pred              # preds are logits
        pred_ids = preds if preds.ndim == 2 else np.argmax(preds, axis=-1)  
        labels = np.where(labels == -100, pad_id, labels)

        pred_txt  = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        label_txt = tokenizer.batch_decode(labels,   skip_special_tokens=True)

        P = [safe_json(t.strip()) for t in pred_txt]
        G = [safe_json(t.strip()) for t in label_txt]

        # Parse/format quality
        json_parse_rate = sum(1 for p in P if p) / max(1,len(P))
        exact_match_rate = sum(1 for p,g in zip(P,G) if p==g and p!={}) / max(1,len(P))

        # Collect fieldwise labels
        dir_y_true, dir_y_pred = [], []
        mag_y_true, mag_y_pred = [], []
        for p,g in zip(P,G):
            for f in DIR_FIELDS:
                if f in g and g[f] is not None and f in p and p[f] is not None:
                    dir_y_true.append(str(g[f]).strip()); dir_y_pred.append(str(p[f]).strip())
            for f in MAG_FIELDS:
                if f in g and g[f] is not None and f in p and p[f] is not None:
                    mag_y_true.append(str(g[f]).strip()); mag_y_pred.append(str(p[f]).strip())

        metrics = {}
        if dir_y_true:
            metrics["eval_direction_acc_macro"] = accuracy_score(dir_y_true, dir_y_pred)
            metrics["eval_direction_f1_macro"]  = f1_score(dir_y_true, dir_y_pred, average="macro", zero_division=0)
        if mag_y_true:
            metrics["eval_magnitude_acc_macro"] = accuracy_score(mag_y_true, mag_y_pred)
            metrics["eval_magnitude_f1_macro"]  = f1_score(mag_y_true, mag_y_pred, average="macro", zero_division=0)

        # Aggregate headline metric for checkpointing
        metrics["eval_avg_macro_f1"] = metrics.get("eval_direction_f1_macro", 0.0)
        if "eval_direction_f1_macro" in metrics and "eval_magnitude_f1_macro" in metrics:
            metrics["eval_avg_direction_f1"] = metrics["eval_direction_f1_macro"]
            metrics["eval_avg_macro_f1"] = 0.5*metrics["eval_direction_f1_macro"] + 0.5*metrics["eval_magnitude_f1_macro"]
        elif "eval_direction_f1_macro" in metrics:
            metrics["eval_avg_direction_f1"] = metrics["eval_direction_f1_macro"]

        metrics["eval_json_parse_rate"]   = json_parse_rate
        metrics["eval_exact_json_match"]  = exact_match_rate
        return metrics

    return compute_metrics


def make_trainer(model, tokenizer, train_ds, val_ds, cfg, out_dir):
    checkpoint_dir = os.environ.get("CHECKPOINT_DIR", out_dir)

    args = TrainingArguments(
    output_dir=checkpoint_dir,
    per_device_train_batch_size=cfg["train"]["per_device_train_batch_size"],
    gradient_accumulation_steps=cfg["train"]["gradient_accumulation_steps"],
    learning_rate=cfg["train"]["learning_rate"],
    num_train_epochs=cfg["train"]["num_train_epochs"],
    weight_decay=cfg["train"]["weight_decay"],
    warmup_ratio=cfg["train"]["warmup_ratio"],
    lr_scheduler_type=cfg["train"]["lr_scheduler_type"],

    #logging_steps=cfg["train"]["logging_steps"],

    save_strategy=cfg["train"]["save_strategy"],
    #save_steps=cfg["train"].get("save_steps"),             
    save_total_limit=cfg["train"]["save_total_limit"],

    evaluation_strategy=cfg["train"]["evaluation_strategy"],
    #eval_steps=cfg["train"].get("eval_steps"),          

    per_device_eval_batch_size=cfg["train"]["per_device_eval_batch_size"],
    eval_accumulation_steps=cfg["train"]["eval_accumulation_steps"],
    
    load_best_model_at_end=cfg["train"]["load_best_model_at_end"],
    bf16=cfg["train"]["bf16"],
    gradient_checkpointing=cfg["train"]["gradient_checkpointing"],
    seed=cfg["train"]["seed"],
    remove_unused_columns=cfg["train"]["remove_unused_columns"],

    dataloader_num_workers= cfg["train"]["dataloader_num_workers"] ,        
    dataloader_pin_memory= cfg["train"]["dataloader_pin_memory"],     
    dataloader_drop_last= cfg["train"]["dataloader_drop_last"],         

    metric_for_best_model=cfg["train"].get("metric_for_best_model","eval_avg_direction_f1"),
    greater_is_better=cfg["train"].get("greater_is_better", True),
    )

    return Trainer(
        model=model,
        args=args,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=None,
        tokenizer=tokenizer,
        compute_metrics=make_compute_metrics(tokenizer),
        preprocess_logits_for_metrics = _preprocess_logits_for_metrics
    )
