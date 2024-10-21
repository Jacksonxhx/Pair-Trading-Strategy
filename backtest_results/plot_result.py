import os
import json
import matplotlib.pyplot as plt


def plot_sharpe_vs_data_points(filename):
    """
    Plots Sharpe Ratio vs. Total Data Points from the JSON data.
    """
    with open(filename, 'r') as f:
        data = json.load(f)

    # Extract Total Data Points and Sharpe Ratio for plotting
    total_data_points = [entry["Total Data Points"] for entry in data]
    sharpe_ratios = [entry["Sharpe Ratio"] for entry in data]
    output_dir = 'graph/'

    # Plot the relationship between Total Data Points and Sharpe Ratio
    plt.figure(figsize=(8, 6))
    plt.plot(total_data_points, sharpe_ratios, marker='o', linestyle='-', color='b', label='Sharpe Ratio')
    plt.title('Relationship between Sharpe Ratio and Total Data Points')
    plt.xlabel('Total Data Points')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(output_dir, f'{filename[5:-5]}.png'))
    plt.show()


if __name__ == "__main__":
    json_file = 'json/time_length.json'

    # Plot the data
    plot_sharpe_vs_data_points(json_file)
