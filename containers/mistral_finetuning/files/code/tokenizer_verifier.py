from src.tokenizer import tokenize_batch
from transformers import AutoTokenizer
from src.prompts import build_prompt, build_target_json
import pandas as pd

# carregar o mesmo tokenizer que usou no treino
tok = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

df = pd.read_csv("./input/training_database.csv")

# constrói colunas prompt/target_json
df["prompt"] = df.apply(build_prompt, axis=1)
df["target_json"] = df.apply(build_target_json, axis=1)

# exemplo mínimo
batch = {
    "prompt": df["prompt"].tolist(),
    "target_json": df["target_json"].tolist()
}

# tokenizar com seu método
out = tokenize_batch(batch, tok, max_inp=512)

# inspecionar o que saiu
ids = out["input_ids"][0].tolist()
labs = out["labels"][0].tolist()

print("=== Decoded input_ids ===")
print(tok.decode(ids))

print("\n=== Decoded labels (ignora -100) ===")
print(tok.decode([i for i, l in zip(ids, labs) if l != -100]))

print("\n=== Labels (numéricos) ===")
print(labs)
