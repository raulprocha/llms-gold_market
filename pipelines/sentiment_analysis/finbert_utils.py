"""FinBERT sentiment analysis utilities for financial news."""

from typing import Any
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline


def sentiment_analysis(
    row: pd.Series,
    model: BertForSequenceClassification,
    tokenizer: BertTokenizer,
    device: torch.device,
    nlp: pipeline
) -> pd.Series:
    """Analyze sentiment of financial headline using FinBERT.
    
    Args:
        row: DataFrame row containing headline and metadata
        model: Pre-trained FinBERT model for sequence classification
        tokenizer: BERT tokenizer instance
        device: PyTorch device (CPU or CUDA)
        nlp: Hugging Face pipeline for text classification
        
    Returns:
        Series containing original data plus sentiment analysis results
        
    Example:
        >>> row = pd.Series({"id": 1, "symbol": "GOLD", "name": "Gold", 
        ...                  "generated_headline": "Gold prices surge"})
        >>> result = sentiment_analysis(row, model, tokenizer, device, nlp)
    """
    id_val = row["id"]
    symbol = row["symbol"]
    symbol_name = row["name"]
    generated_headline = row["generated_headline"]
    prompt = [generated_headline]

    generated = nlp(prompt, model, tokenizer, device)

    return pd.Series({
        "id": id_val,
        "symbol": symbol,
        "symbol_name": symbol_name,
        "generated_headline": generated_headline,
        "sentiment": generated,
    })
