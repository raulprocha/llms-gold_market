# src/model.py
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
import torch

def load_model_tokenizer(cfg, cache_dir):
    tok = AutoTokenizer.from_pretrained(
        cfg["model"]["name"], trust_remote_code=True, use_fast=False, cache_dir=cache_dir
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    # 1. Carrega o modelo em 4-bit ou full precision
    if cfg["model"]["load_in_4bit"]:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        mdl = AutoModelForCausalLM.from_pretrained(
            cfg["model"]["name"],
            cache_dir=cache_dir,
            device_map="auto",
            quantization_config=bnb_config,
            trust_remote_code=True,
        )
    else:
        mdl = AutoModelForCausalLM.from_pretrained(
            cfg["model"]["name"],
            cache_dir=cache_dir,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )

    # 2. Preparar p/ treino em k-bit + gradient checkpointing
    mdl.config.use_cache = False
    mdl = prepare_model_for_kbit_training(mdl, use_gradient_checkpointing=True)
    mdl.gradient_checkpointing_enable()
    try:
        mdl.enable_input_require_grads()
    except Exception:
        pass  # nem todo modelo expõe isso

    # 3. Aplica LoRA
    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=cfg["lora"]["r"],
        lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        target_modules=cfg["lora"]["target_modules"],
        inference_mode=False,
        bias="none",
    )
    mdl = get_peft_model(mdl, lora)

    return mdl, tok
