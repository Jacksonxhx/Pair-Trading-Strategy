import json
import matplotlib.pyplot as plt


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def plot_sharpe_vs_data_points(data):
    """
    Plots Sharpe Ratio vs. Total Data Points from the JSON data.
    """
    # Extract Total Data Points and Sharpe Ratio for plotting
    total_data_points = [entry["Total Data Points"] for entry in data]
    sharpe_ratios = [entry["Sharpe Ratio"] for entry in data]

    # Plot the relationship between Total Data Points and Sharpe Ratio
    plt.figure(figsize=(8, 6))
    plt.plot(total_data_points, sharpe_ratios, marker='o', linestyle='-', color='b', label='Sharpe Ratio')
    plt.title('Relationship between Sharpe Ratio and Total Data Points')
    plt.xlabel('Total Data Points')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    json_file = 'backtest_results_time_length_ratio_5.json'
    data = read_json(json_file)

    # Plot the data
    plot_sharpe_vs_data_points(data)
