""" finbert"""
import pandas as pd

def sentiment_analysis(new, model, tokenizer, device, nlp):
  id = new["id"]
  symbol = new["symbol"]
  symbol_name = new["name"]
  generated_headline = new["generated_headline"]
  prompt = [generated_headline]

  generated = nlp(prompt, model, tokenizer, device)

  return pd.Series({
      "id": id,
      "symbol": symbol,
      "symbol_name": symbol_name,
      "generated_headline": generated_headline,
      "sentiment": generated,
  })
