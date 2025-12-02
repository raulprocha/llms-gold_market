"""Prompt engineering utilities for gold price prediction model."""

import json
from typing import Dict, Any
import pandas as pd


def build_prompt(row: pd.Series) -> str:
    """Build training prompt from news and market data.
    
    Constructs a structured prompt containing news headline, sentiment
    analysis, and market status information for multi-horizon prediction.
    
    Args:
        row: DataFrame row with news, sentiment, and market data
        
    Returns:
        Formatted prompt string for model training/inference
        
    Example:
        >>> row = pd.Series({
        ...     "generated_headline": "Gold prices surge",
        ...     "label": "Positive",
        ...     "sentiment_strength": "0.95",
        ...     "explanation": "Strong bullish sentiment",
        ...     "symbol": "GLD",
        ...     "symbol_name": "Gold ETF",
        ...     "market_closed_verifier": "Open",
        ...     "market_closed_verifier_6h": "Open",
        ...     # ... other fields
        ... })
        >>> prompt = build_prompt(row)
    """
    return (
        f"News: {row['generated_headline']}\n"
        f"Sentiment: {row['label']} ({row['sentiment_strength']})\n"
        f"Explanation: {row['explanation']}\n"
        f"Asset Context:\n"
        f"- Symbol: {row['symbol']} ({row['symbol_name']})\n"
        f"Market status:\n"
        f"- Was the market open at time of news? {row['market_closed_verifier']}\n"
        f"- Will the market be open during future impact windows?\n"
        f"    • 6h later: {row['market_closed_verifier_6h']}\n"
        f"    • 12h later: {row['market_closed_verifier_12h']}\n"
        f"    • 24h later: {row['market_closed_verifier_24h']}\n"
        f"    • 48h later: {row['market_closed_verifier_48h']}\n"
        "Respond ONLY with a compact JSON using keys: "
        "\"direction_6h\",\"magnitude_6h\",\"direction_12h\",\"magnitude_12h\","
        "\"direction_24h\",\"magnitude_24h\",\"direction_48h\",\"magnitude_48h\".\n"
        "Directions: \"Up\"|\"Down\"|\"Neutral\". "
        "Magnitudes: \"low impact\"|\"medium-low impact\"|\"medium-high impact\"|\"high impact\"."
    )


def build_target_json(row: pd.Series) -> str:
    """Build target JSON string from prediction labels.
    
    Converts multi-horizon direction and magnitude predictions into
    compact JSON format for model training.
    
    Args:
        row: DataFrame row with direction and magnitude columns
        
    Returns:
        JSON string with prediction targets
        
    Example:
        >>> row = pd.Series({
        ...     "direction_6h": "Up",
        ...     "magnitude_6h": "medium-high impact",
        ...     "direction_12h": "Up",
        ...     "magnitude_12h": "high impact",
        ...     # ... other horizons
        ... })
        >>> target = build_target_json(row)
        >>> print(target)
        {"direction_6h":"Up","magnitude_6h":"medium-high impact",...}
    """
    payload = {
        "direction_6h": row["direction_6h"],
        "magnitude_6h": row["magnitude_6h"],
        "direction_12h": row["direction_12h"],
        "magnitude_12h": row["magnitude_12h"],
        "direction_24h": row["direction_24h"],
        "magnitude_24h": row["magnitude_24h"],
        "direction_48h": row["direction_48h"],
        "magnitude_48h": row["magnitude_48h"],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
