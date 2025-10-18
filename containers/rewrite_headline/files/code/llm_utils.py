""" Rewrite headline with LLM"""

from bs4 import BeautifulSoup
import pandas as pd
import torch

def generate_response(prompt, model, tokenizer, device, max_new_tokens=256):
  inputs = tokenizer(prompt, return_tensors='pt').to(device)
  with torch.no_grad():
      output = model.generate(**inputs, max_new_tokens = max_new_tokens, use_cache =True, pad_token_id = tokenizer.eos_token_id)
  output_decoded = tokenizer.decode(output[0], skip_special_tokens =True)
  result = output_decoded.split('[/INST]')[-1].split('\n')[0].strip()
  return result

def rewrite_headline(new, model, tokenizer, device):
  symbol = new["symbol"]
  symbol_name = new["name"]
  headline = new["headline"]
  content = new["content"]
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
  prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

  generated = generate_response(prompt, model, tokenizer, device)

  return pd.Series({
      "symbol": symbol,
      "symbol_name": symbol_name,
      "headline": headline,
      "generated_headline": generated,
  })
