import os
import pandas as pd

def prepare_paths(is_sagemaker: bool):
    if is_sagemaker:
        return (
            "/opt/ml/processing/input/headline_news.csv",
            "/opt/ml/processing/output/predictions.csv",
            "/opt/ml/processing/model",
            "/opt/ml/processing/cache",
        )
    else:
        os.makedirs("output", exist_ok=True)
        return (
            "input/training_database.csv",
            "output/predictions.csv",
            "./adapter",
            "./cache",
        )

def append_row(row_dict, output_path, header_written):
    pd.DataFrame([row_dict]).to_csv(
        output_path, index=False, mode="a", header=not header_written
    )
