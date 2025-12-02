"""LLM utilities for headline rewriting using Mistral-7B."""

from typing import List, Dict, Any
import pandas as pd
import torch
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForCausalLM


def generate_response(
    prompt: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: torch.device,
    max_new_tokens: int = 256
) -> str:
    """Generate text response from LLM given a prompt.
    
    Args:
        prompt: Input text prompt for the model
        model: Pre-trained causal language model
        tokenizer: Tokenizer matching the model
        device: PyTorch device (CPU or CUDA)
        max_new_tokens: Maximum number of tokens to generate
        
    Returns:
        Generated text response, cleaned and trimmed
        
    Note:
        Uses greedy decoding with caching enabled for efficiency.
    """
    inputs = tokenizer(prompt, return_tensors='pt').to(device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id
        )
    output_decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    result = output_decoded.split('[/INST]')[-1].split('\n')[0].strip()
    return result


def rewrite_headline(
    row: pd.Series,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: torch.device
) -> pd.Series:
    """Rewrite financial headline to focus on specific symbol.
    
    Takes a generic financial headline and rewrites it to emphasize
    the impact on a specific trading symbol, using article content
    as additional context.
    
    Args:
        row: DataFrame row containing symbol, headline, and content
        model: Pre-trained Mistral-7B model
        tokenizer: Mistral tokenizer
        device: PyTorch device (CPU or CUDA)
        
    Returns:
        Series with original data plus generated headline
        
    Example:
        >>> row = pd.Series({
        ...     "symbol": "GLD",
        ...     "name": "Gold ETF",
        ...     "headline": "Commodities rally on inflation fears",
        ...     "content": "<p>Gold prices surge...</p>"
        ... })
        >>> result = rewrite_headline(row, model, tokenizer, device)
    """
    symbol = row["symbol"]
    symbol_name = row["name"]
    headline = row["headline"]
    content = row["content"]
    
    # Clean HTML from content
    content = BeautifulSoup(content, "html.parser").get_text() if pd.notna(content) else ''
    
    messages = [
        {
            "role": "user",
            "content": (
                f"Rewrite the headline to focus only on the symbol {symbol} ({symbol_name}).\n "
                f"You may infer details from the context if needed. The new headline should be short, impactful, and relevant to investors.\n\n"
                f"Return only the rewritten headline. Do not add any summary, explanation or note. \n\n "
                f"Original Headline: {headline}\n"
                f"Context: {content}"
            )
        }
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    generated = generate_response(prompt, model, tokenizer, device)

    return pd.Series({
        "symbol": symbol,
        "symbol_name": symbol_name,
        "headline": headline,
        "generated_headline": generated,
    })
