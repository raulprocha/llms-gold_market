"""Inference utilities for gold price prediction."""

import json
from typing import Dict, Any, Union
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def generate_json_response(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: torch.device,
    max_new_tokens: int = 256
) -> Dict[str, Any]:
    """Generate JSON prediction from model given a prompt.
    
    Applies chat template, generates response, and parses JSON output.
    Falls back to raw prediction if JSON parsing fails.
    
    Args:
        prompt: Input prompt with news and market context
        model: Fine-tuned Mistral model for predictions
        tokenizer: Mistral tokenizer
        device: PyTorch device (CPU or CUDA)
        max_new_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with prediction keys (direction_6h, magnitude_6h, etc.)
        or {"raw_prediction": str} if JSON parsing fails
        
    Example:
        >>> prompt = "News: Gold prices surge\\nSentiment: Positive..."
        >>> prediction = generate_json_response(prompt, model, tokenizer, device)
        >>> print(prediction["direction_6h"])
        "Up"
    """
    conv = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        conv,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(text, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    decoded = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        return {"raw_prediction": decoded}
