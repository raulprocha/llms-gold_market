import os, torch, gc
import pandas as pd
from tqdm import tqdm

from src.inference import load_lora_model
from src.utils import generate_json_response
from src.prompts import build_prompt, build_target_json
from src.data import prepare_paths, append_row

is_sagemaker = "SM_MODEL_DIR" in os.environ
input_path, output_path, adapter_dir, cache_dir = prepare_paths(is_sagemaker)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
head_rows = os.environ.get("NUM_ROWS")

if __name__ == "__main__":
    model, tokenizer = load_lora_model(
        base_model="mistralai/Mistral-7B-Instruct-v0.2",
        adapter_dir=adapter_dir,
        cache_dir=cache_dir,
    )

    df = pd.read_csv(input_path)
    df = df.head(int(head_rows))
    header_written = os.path.exists(output_path)

    for _, row in tqdm(df.iterrows(), total=len(df), desc="🚀 Inference"):
        try:
            prompt = build_prompt(row)
            prediction = generate_json_response(prompt, model, tokenizer, device)
        except Exception as e:
            prediction = {"error": str(e)}

        out = {
            "symbol": row.get("symbol", ""),
            "headline": row.get("headline", ""),
            "target": build_target_json(row),
            "prediction": prediction,
        }
        append_row(out, output_path, header_written)
        header_written = True

        torch.cuda.empty_cache()
        gc.collect()

    print("✅ Finished. Saved to:", output_path)
