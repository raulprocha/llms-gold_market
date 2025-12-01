# src/prompts.py
import json

def build_prompt(row):
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

def build_target_json(row):
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
