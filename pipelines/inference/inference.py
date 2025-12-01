import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


def load_lora_model(base_model: str, adapter_dir: str, cache_dir: str):
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True, use_fast=False)
    quant_config = BitsAndBytesConfig(
        load_in_4_bit =True,
        bnb_4bit_compute_dtype = "float16",
        bnb_4bit_use_double_quant = True, 
        bnb_4bit_quant_type ="nf4"
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        dtype=torch.float16,
        quantization_config= quant_config,
        offload_folder="offload",
        device_map="auto",
        cache_dir=cache_dir,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, adapter_dir)
    return model, tokenizer
