from src.prompts import build_prompt, build_target_json
import pandas as pd 

df = pd.read_csv('input/training_database.csv')

to_file = []
for i in range(20):
    to_file.append({
        "prompt": build_prompt(df.iloc[i]),
        "target": build_target_json(df.iloc[i])
    })

pd.DataFrame(to_file).to_csv('samples.csv', index=False)