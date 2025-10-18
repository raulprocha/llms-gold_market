# src/tokenizer.py
from copy import deepcopy
import torch

def tokenize_batch(batch, tokenizer, max_inp):
    # 1) Read raw fields
    def flatten_messages(msgs):
        if isinstance(msgs, list):
            return "\n".join([f"{m['role']}: {m['content']}" for m in msgs])
        return msgs  # já é string

    prompts = [flatten_messages(p) for p in batch["prompt"]]
    targets = batch["target_json"]

    # 2) Build one-turn conversations
    full_conv = [
        [
            {"role": "user", "content": f"{p}\n\nRespond with only this JSON:"},
            {"role": "assistant", "content": t},
        ]
    for p, t in zip(prompts, targets)]
    user_only = [[{"role": "user", "content": f"{p}\n\nRespond with only this JSON:"}] for p in prompts]

    # 3) Render chat templates to text
    full_texts = [
        tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=False)
        for conv in full_conv
    ]
    user_texts = [
        tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=False)
        for conv in user_only
    ]

    # 4) Tokenize to lists (no tensors here; we’ll tensorize at the end)
    full_tok = tokenizer(full_texts, truncation=True, max_length=max_inp, padding=False)
    user_tok = tokenizer(user_texts,  truncation=True, max_length=max_inp, padding=False)

    # 5) Mask the user part in labels
    input_ids, labels, attention_mask = [], [], []
    for ids, am, uids in zip(full_tok["input_ids"], full_tok["attention_mask"], user_tok["input_ids"]):
        # Ensure flat-int lists (defensive)
        ids  = [int(x) for x in ids]
        am   = [int(x) for x in am]
        uids = [int(x) for x in uids]

        L_user = len(uids)
        lab = ids.copy()
        for i in range(min(L_user, len(lab))):
            lab[i] = -100

        input_ids.append(ids)
        labels.append(lab)
        attention_mask.append(am)

    # 6) Use a single, global fixed length for all samples
    max_len = max_inp

    # 7) Determine padding ids
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        # Common fallback for decoder-only LMs (e.g., Mistral/LLaMA)
        pad_id = tokenizer.eos_token_id
    if pad_id is None:
        raise ValueError("Tokenizer must have pad_token_id or eos_token_id set for padding.")

    # 8) Right-pad all sequences to max_len
    input_ids_padded = [ids + [pad_id] * (max_len - len(ids)) for ids in input_ids]
    attention_mask_padded = [am + [0] * (max_len - len(am)) for am in attention_mask]
    labels_padded = [lab + [-100] * (max_len - len(lab)) for lab in labels]

    # 9) Convert to tensors (long)
    batch_out = {
        "input_ids": torch.tensor(input_ids_padded, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask_padded, dtype=torch.long),
        "labels": torch.tensor(labels_padded, dtype=torch.long),
    }
    return batch_out
