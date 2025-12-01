# src/data.py
import pandas as pd
from sklearn.model_selection import train_test_split
from src.prompts import build_prompt, build_target_json
from datasets import Dataset

def load_dataset(csv_path):
    df = pd.read_csv(csv_path)
    df= df.head(100)
    # constrói colunas prompt/target_json
    df["prompt"] = df.apply(build_prompt, axis=1)
    df["target_json"] = df.apply(build_target_json, axis=1)

    train_val_df, test_df = train_test_split(df, test_size=0.05, random_state=42)
    train_df, val_df = train_test_split(train_val_df, test_size=0.05/0.95, random_state=42)

    test_ds = Dataset.from_pandas(test_df)
    train_ds = Dataset.from_pandas(train_df)
    val_ds = Dataset.from_pandas(val_df)

    return test_ds, train_ds, val_ds