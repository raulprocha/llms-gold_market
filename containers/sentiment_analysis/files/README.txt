==============================
TCC Project Summary – LLM + RAG for Financial Market Forecasting
==============================

✅ PROJECT GOAL
------------------------------
Train an LLM to predict the direction and magnitude of XAU/USD impact after a news release, using:
- Supervised fine-tuning with structured JSON output
- RAG (Retrieval-Augmented Generation) to handle new, unseen news during inference

📦 TRAINING DATA PREPARED
------------------------------
Each row represents a headline generated for a specific asset (symbol), including:
- generated_headline (via Mistral, asset-specific)
- sentiment label and score (via FinBERT)
- direction_*h and magnitude_*h based on future XAU/USD prices (from Metatrader + Athena)

Magnitude scaled between 0 and 5 using:
- 6h  → divisor 0.3
- 12h → divisor 0.5
- 24h → divisor 0.7
- 48h → divisor 1.2

🎯 FINE-TUNING FORMAT
------------------------------
Selected model: FinTral-7B (https://huggingface.co/numerai/FinTral-7B-v0.1)

Prompt (input):
-----------------
News: {generated_headline}
Sentiment: {label} ({score})
Target 6h: direction {direction_6h}, magnitude {magnitude_6h}
Target 12h: direction {direction_12h}, magnitude {magnitude_12h}
Target 24h: direction {direction_24h}, magnitude {magnitude_24h}
Target 48h: direction {direction_48h}, magnitude {magnitude_48h}

Reply in JSON format with the following keys:
"direction_6h","magnitude_6h","direction_12h","magnitude_12h","direction_24h","magnitude_24h","direction_48h","magnitude_48h"

Target (expected output):
------------------------
{
  "direction_6h": "...",
  "magnitude_6h": ...,
  "direction_12h": "...",
  "magnitude_12h": ...,
  "direction_24h": "...",
  "magnitude_24h": ...,
  "direction_48h": "...",
  "magnitude_48h": ...
}

🧠 POST-TRAINING (INFERENCE)
------------------------------
Input: New financial news mentioning a relevant asset (gold or USD-related).

Pipeline (LangChain or manual):
1. Embed the new news article
2. Retrieve related context using Pinecone (or FAISS)
3. Generate headline and sentiment using Mistral + FinBERT
4. Pass to the fine-tuned model to get:
   - Expected direction (Up, Down, Neutral)
   - Magnitude (0 to 5) for 6h, 12h, 24h, 48h horizons

🛠️ TOOLS & TECHNOLOGIES
------------------------------
- LLM: FinTral-7B (based on Mistral)
- Sentiment Analysis: FinBERT (yiyanghkust/finbert-tone)
- Embedding model: e5-finance (or similar)
- Vector DB: Pinecone
- Infrastructure: AWS SageMaker (likely using LoRA on 4x 24GB GPUs)
- SQL Extraction: Amazon Athena (for candles and news)
- Optional Orchestration: LangChain
