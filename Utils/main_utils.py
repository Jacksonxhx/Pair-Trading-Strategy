import json
import os
import yaml


def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def is_duplicate(entry, results):
    """
    Check if a given entry is already present in the results.

    Parameters:
    -----------
    entry : dict
        The new entry to be checked.
    results : list of dict
        The existing results to check against.

    Returns:
    --------
    bool
        True if the entry is a duplicate, False otherwise.
    """
    for result in results:
        # Compare relevant fields
        if (
            result['Time Length (days)'] == entry['Time Length (days)'] and
            result['Total Data Points'] == entry['Total Data Points'] and
            result['Training Ratio (%)'] == entry['Training Ratio (%)'] and
            result['Testing Ratio (%)'] == entry['Testing Ratio (%)'] and
            result['Model'] == entry['Model'] and
            result['Window'] == entry['Window'] and
            result['Threshold'] == entry['Threshold'] and
            result['Sharpe Ratio'] == entry['Sharpe Ratio'] and
            result['Annual Return (%)'] == entry['Annual Return (%)']
        ):
            return True
    return False


def save_backtest_results(config, performance, total_datapoints, result_dir='backtest_results.json'):
    """
    Save the backtest results in JSON format for future reference.
    """

    # Extract relevant data
    total_datapoints = total_datapoints
    time_length = config['data']['time_length_days']
    training_ratio = 1 - 1 / config['data']['training_threshold']
    testing_ratio =  1 / config['data']['training_threshold']
    model = "Linear Regression"  # Assuming we are using linear regression model, adjust if necessary
    window = config['strategy']['window']
    threshold = config['strategy']['z_threshold']
    sharp_ratio = performance.get('Sharpe Ratio', None)
    annual_r = performance.get('Annualized Return (%)', None)

    # Prepare a dictionary with the relevant information
    backtest_entry = {
        "Time Length (days)": time_length,
        "Total Data Points": total_datapoints,
        "Training Ratio (%)": training_ratio,
        "Testing Ratio (%)": testing_ratio,
        "Model": model,
        "Window": window,
        "Threshold": threshold,
        "Sharpe Ratio": sharp_ratio,
        "Annual Return (%)": annual_r
    }

    if os.path.exists(result_dir):
        # If exists, load the existing data
        with open(result_dir, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, initialize results as an empty list
                results = []
    else:
        # If not, initialize a new list
        results = []

        # Check for duplicates before appending
    if not is_duplicate(backtest_entry, results):
        # Append the new entry if it's not a duplicate
        results.append(backtest_entry)
        # Save the updated results back to the JSON file
        with open(result_dir, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"New backtest results appended to {result_dir}.")
    else:
        print("Duplicate entry found. No new results were added.")