import pandas as pd
import json
import os

results_folder = "results"

def json_to_md(input_file: str, output_file:str):
    rows = []
    with open(os.path.join(results_folder, input_file), 'r') as f:
        json_data = json.load(f)

    for weight, levels in json_data.items():
        for level, details in levels.items():
            row = {
                'weight': weight,
                'level': level,
                'elapsed_time': f"{details['elapsed_time']:.2f}",
                'b_factor': f"{details['b_factor']:.2f}",
                'length': details['length']
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    print(df)

    df.to_markdown(os.path.join(results_folder, output_file), index=False)

if __name__ == '__main__':
    json_to_md('results.json', 'results.md')
