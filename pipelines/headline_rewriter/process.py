import warnings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
from llm_utils import rewrite_headline
import pandas as pd
import os
import gc
from huggingface_hub import login
import shutil
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

tqdm.pandas()

# Login to Hugging Face Hub securely
hf_token = os.getenv("HF_API_TOKEN")
if hf_token:
    login(hf_token)
else:
    raise ValueError("❌ Missing HF_API_TOKEN in environment variables")

# Disable warnings and telemetry
warnings.filterwarnings("ignore")

is_sage_maker = "SM_MODEL_DIR" in os.environ

if is_sage_maker:
    # Look for paths
    for root, dirs, files in os.walk('/opt/ml/processing'):
        print(f"Pasta: {root}")
        for file in files:
            print(f"-> {file}")
    input_path = '/opt/ml/processing/input/headline_news.csv'
    output_path = '/opt/ml/processing/output/output_headline_news_missing.csv'
    cache_dir = "/opt/ml/processing/cache"
    print("Running in SageMaker")

else:
    input_path = 'input/headline_news.csv'
    output_path = 'output/output_headline_news.csv'
    cache_dir = './cache'
    print("Running Local")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = 'mistralai/Mistral-7B-Instruct-v0.2'

if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        use_fast=False,
        cache_dir=cache_dir
    )
    print("Tokenizer loaded successfully")

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        cache_dir=cache_dir,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    print("Model loaded successfully")

    # Main input dataframe
    df = pd.read_csv(input_path)

    head_rows = os.environ.get("NUM_ROWS", None)

    # Look for processed rows in output file
    if os.path.exists(output_path):
        processed_rows = sum(1 for _ in open(output_path)) - 1
    else:
        processed_rows = 0

    # Define which rows still need to be processed
    header_written = os.path.exists(output_path)

    if head_rows == 'ALL':
        rows_to_process = df.iloc[processed_rows:]
    elif head_rows is not None:
        rows_to_process = df.iloc[processed_rows:int(head_rows)]
    else:
        raise ValueError('NUM_ROWS must be defined as ALL or a number')

    # Main loop
    not is_sage_maker and os.makedirs('output', exist_ok=True)
    for _, row in tqdm(
        rows_to_process.iterrows(),
        total=len(rows_to_process),
        desc="\n Rewrite headline bar progress"
    ):
        try:
            result = rewrite_headline(row, model, tokenizer, device)
        except Exception as e:
            print(f"Erro na linha {row.name}: {e}")
            result = pd.Series({
                "symbol": row.get("symbol", ""),
                "symbol_name": row.get("name", ""),
                "headline": row.get("headline", ""),
                "generated_headline": "[ERROR]",
            })

        result.to_frame().T.to_csv(
            output_path, index=False, mode='a', header=not header_written
        )
        header_written = True

        torch.cuda.empty_cache()
        gc.collect()

    tqdm.write("✅ Output successfully saved.")
