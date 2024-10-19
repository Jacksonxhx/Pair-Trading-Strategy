import os
from datetime import time

import pandas as pd


def load_data_from_json(filepath):
    """
    Loads data from a JSON file into a DataFrame.
    """
    if os.path.exists(filepath):
        data = pd.read_json(filepath, orient='index')
        data.index = pd.to_datetime(data.index)
        print(f"Data loaded from {filepath}")
        return data
    else:
        return None


def save_data_to_json(data, filepath):
    """
    Saves the DataFrame to a JSON file.
    """
    data_to_save = data.copy()
    data_to_save.index = data_to_save.index.astype(str)
    data_to_save.to_json(filepath, orient='index')
    print(f"Data saved to {filepath}")


def adjust_to_trading_hours(start_date, end_date):
    """
    Adjust the start and end date to match market trading hours: 9:30 to 15:59.
    """
    market_open = time(9, 30)
    market_close = time(15, 59)

    # Adjust the start date to 9:30 AM if it's earlier or doesn't specify the time
    if start_date.time() < market_open:
        start_date = start_date.replace(hour=9, minute=30, second=0, microsecond=0)

    # Adjust the end date to 15:59 PM if it's later or doesn't specify the time
    if end_date.time() > market_close:
        end_date = end_date.replace(hour=15, minute=59, second=0, microsecond=0)

    return start_date, end_date