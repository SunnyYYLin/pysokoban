import json
import pandas as pd
import matplotlib.pyplot as plt

def json_to_dataframe(json_data):
    """
    将JSON数据转换为DataFrame。

    参数:
        json_data (dict): JSON数据

    返回:
        pd.DataFrame: 数据Frame
    """
    rows = []

    for weight, levels in json_data.items():
        for level, details in levels.items():
            row = {
                'weight': 10000 if weight == "Infinity" else float(weight),
                'level': int(level),
                'elapsed_time': details['elapsed_time'],
                'b_factor': details['b_factor'],
                'length': details['length']
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    return df

def plot_analysis(df):
    """
    分析数据并使用matplotlib绘制图表。

    参数:
        df (pd.DataFrame): 数据Frame

    返回:
        None
    """
    levels = df['level'].unique()
    weights = sorted(df['weight'].unique())

    plt.figure(figsize=(14, 7))

    # 绘制 b_factor 随 b_weight 变化的曲线
    plt.subplot(1, 2, 1)
    for level in levels:
        level_data = df[df['level'] == level]
        plt.plot(level_data['weight'], level_data['b_factor'], marker='o', label=f'Level {level}')
    plt.xscale('log')
    plt.xlabel('b_weight')
    plt.ylabel('b_factor')
    plt.title('b_factor vs b_weight')
    plt.xticks([1, 10, 100, 1000, 10000], ['1', '10', '100', '1000', 'Infinity'])
    plt.legend()

    # 绘制 elapsed_time 随 b_weight 变化的曲线
    plt.subplot(1, 2, 2)
    for level in levels:
        level_data = df[df['level'] == level]
        plt.plot(level_data['weight'], level_data['elapsed_time'], marker='o', label=f'Level {level}')
    plt.xscale('log')
    plt.xlabel('b_weight')
    plt.ylabel('elapsed_time')
    plt.title('elapsed_time vs b_weight')
    plt.xticks([1, 10, 100, 1000, 10000], ['1', '10', '100', '1000', 'Infinity'])
    plt.legend()

    plt.tight_layout()
    plt.show()
    
if __name__ == '__main__':
    with open('results/results.json', 'r') as f:
        json_data = json.load(f)
    df = json_to_dataframe(json_data)
    plot_analysis(df)