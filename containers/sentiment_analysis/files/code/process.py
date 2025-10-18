import warnings
import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from finbert_utils import sentiment_analysis
from tqdm import tqdm
import pandas as pd
import os
import gc

tqdm.pandas()

warnings.filterwarnings("ignore")

is_sage_maker = "SM_MODEL_DIR" in os.environ

if is_sage_maker:
    #Look for paths
    for root, dirs, files in os.walk('/opt/ml/processing'):
        print(f"Pasta: {root}")
        for file in files:
            print(f"-> {file}")
    input_path = '/opt/ml/processing/input/generated_headline-to_finbert.csv'
    output_path = '/opt/ml/processing/output/output_finbert.csv'
    cache_dir = "/opt/ml/processing/cache"
    print("Running in Sagemaker")

else:
    input_path = 'input/generated_headline-to_finbert.csv'
    output_path = 'output/output_finbert.csv'
    cache_dir = './cache'
    print("Running Local")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = 'yiyanghkust/finbert-tone'

if __name__ == "__main__":
    tokenizer = BertTokenizer.from_pretrained(model_name, use_fast=False, cache_dir = cache_dir)
    print("Tokenizer carregado")
    model = BertForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir, torch_dtype=torch.float16).to(device)
    print("Modelo carregado")
    nlp = pipeline("text-classification", model=model_name, tokenizer = tokenizer)

    # Main input dataframe
    df = pd.read_csv(input_path)

    head_rows = os.environ.get("NUM_ROWS", None)
    
    # Look for processed rows in outup file
    if os.path.exists(output_path):
        processed_rows = sum(1 for _ in open(output_path)) -1
    else:
        processed_rows = 0
    

    # Define which rows still need to be processed
    header_written = os.path.exists(output_path)

    if head_rows =='ALL':
        rows_to_process = df.iloc[processed_rows:]
    elif head_rows is not None:
        rows_to_process = df.iloc[processed_rows:int(head_rows)]
    else:
         raise ValueError('NUM_ROWS must be defined as ALL or a number')
           
    # main loop
    result_list = []
    not is_sage_maker and os.makedirs('output', exist_ok=True) 
    for _, row in tqdm(rows_to_process.iterrows(), total = len(rows_to_process), desc = "\n Finbert bar progress"):
        try:
            result = sentiment_analysis(row, model, tokenizer, device, nlp)
        except Exception as e:
            print(f"Erro na linha {row.name}: {e}")
            result = pd.Series({
            "id": row.get("id", ""),
            "symbol": row.get("symbol", ""),
            "symbol_name": row.get("name", ""),
            "generated_headline": row.get("generated_headline", ""),
            "sentiment" : "[ERROR]"
            })
        
        result.to_frame().T.to_csv(output_path, index=False, mode='a', header=not header_written) 
        header_written = True

        torch.cuda.empty_cache()
        gc.collect()
    
    tqdm.write("Output gravado")
