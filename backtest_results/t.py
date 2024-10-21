import json
import os

def sort_json_by_sharpe(filename):
    """
    Sorts the JSON data by 'Sharpe Ratio' in descending order.
    """
    # 读取 JSON 文件
    with open(filename, 'r') as f:
        data = json.load(f)

    # 检查 'Sharpe Ratio' 是否存在于所有条目中
    if not all('Sharpe Ratio' in entry for entry in data):
        raise KeyError("Some entries are missing the 'Sharpe Ratio' key.")

    # 按照 'Sharpe Ratio' 进行排序，降序排列
    sorted_data = sorted(data, key=lambda x: x['Sharpe Ratio'], reverse=True)

    # 输出排序后的结果文件
    sorted_filename = f"sorted_{os.path.basename(filename)}"
    with open(sorted_filename, 'w') as f:
        json.dump(sorted_data, f, indent=4)

    print(f"Sorted JSON data saved to {sorted_filename}")


if __name__ == "__main__":
    # 输入 JSON 文件路径，替换为你实际的 JSON 文件路径
    json_file = 'json/all.json'

    # 对 JSON 数据进行排序并保存
    sort_json_by_sharpe(json_file)
