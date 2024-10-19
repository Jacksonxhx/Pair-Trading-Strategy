from ib_insync import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os
import json

from Data.utils import load_data_from_json, save_data_to_json, adjust_to_trading_hours


class DataLoader:
    """
    Fetches historical price data for given symbols between start_date and end_date using the IB API.
    Handles API limitations by fetching data in chunks and respecting rate limits.
    Now includes functionality to save data to and load data from local JSON files.
    """

    def __init__(self, ib_port=7497, client_id=1, data_dir='Data/commodity_data/'):
        self.ib_port = ib_port
        self.client_id = client_id
        self.ib = None
        self.data_dir = data_dir
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def connect(self):
        """
        Establishes connection to the IB API.
        """
        if not self.ib or not self.ib.isConnected():
            self.ib = IB()
            self.ib.connect('127.0.0.1', self.ib_port, clientId=self.client_id)

    def disconnect(self):
        """
        Disconnects from the IB API.
        """
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()

    def get_data_filename(self, symbol, bar_size):
        """
        Generates a filename for saving the data based on symbol and bar size.
        """
        filename = f"{symbol}_{bar_size.replace(' ', '')}.json"
        filepath = os.path.join(self.data_dir, filename)
        return filepath

    def fetch_data_from_ib(self, symbol, start_date, end_date, bar_size='1 min', what_to_show='TRADES', use_rth=True):
        """
        Fetches new data from IB API (this is the original function provided by you).
        """
        # Call the original fetch_data method (from your provided code)
        return self.fetch_new_data(symbol, start_date, end_date, bar_size, what_to_show, use_rth)

    def fetch_data(self, symbol, start_date, end_date, bar_size='1 min', what_to_show='TRADES', use_rth=True):
        """
        Fetches historical price data for the specified symbol and date range.
        Uses local cache if available, fetches missing data from IB API if needed.
        """
        start_date, end_date = adjust_to_trading_hours(start_date, end_date)

        filepath = self.get_data_filename(symbol, bar_size)
        cached_data = load_data_from_json(filepath)

        if cached_data is not None:
            # Get cached data range
            cached_start = cached_data.index.min()
            cached_end = cached_data.index.max()

            if cached_start <= start_date and cached_end >= end_date:
                print(f"Returning cached data for {symbol} from {start_date} to {end_date}.")
                return cached_data[(cached_data.index >= start_date) & (cached_data.index <= end_date)]

        print(f"Fetching new data for {symbol} from {start_date} to {end_date}.")
        new_data = self.fetch_data_from_ib(symbol, start_date, end_date, bar_size, what_to_show, use_rth)

        if cached_data is not None:
            cached_data = pd.concat([cached_data, new_data])
            cached_data.sort_index(inplace=True)
        else:
            cached_data = new_data

        save_data_to_json(cached_data, filepath)

        return cached_data[(cached_data.index >= start_date) & (cached_data.index <= end_date)]

    # The existing fetch_data method you provided
    def fetch_new_data(self, symbol, start_date, end_date, bar_size='1 min', what_to_show='TRADES', use_rth=True):
        """
        Fetches historical price data for the specified symbol and date range.
        Now checks for local JSON file before fetching.
        """
        try:
            self.connect()

            # Define the contract
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)

            # Determine the maximum duration per request based on bar size
            if bar_size == '1 min':
                max_duration = timedelta(days=30)  # IB limit for 1-min bars
                duration_str_template = '{} D'
                sleep_interval = 3  # seconds
            elif bar_size == '1 day':
                max_duration = timedelta(days=365)  # IB limit for daily bars
                duration_str_template = '{} D'
                sleep_interval = 3  # seconds
            else:
                raise ValueError(f"Unsupported bar size: {bar_size}")

            data_frames = []
            current_end_date = end_date

            while current_end_date > start_date:
                # Calculate the duration to fetch
                remaining_duration = current_end_date - start_date
                fetch_duration = min(remaining_duration, max_duration)

                if fetch_duration.days < 1:
                    print(f"Fetch duration less than 1 day for {symbol}. Ending data fetch.")
                    break

                duration_str = duration_str_template.format(fetch_duration.days)

                # Format the endDateTime as required by IB API (YYYYMMDD HH:MM:SS)
                end_datetime_str = current_end_date.strftime('%Y%m%d %H:%M:%S')

                print(f"Fetching data for {symbol} from {end_datetime_str} back {duration_str}.")

                # Request historical data
                bars = self.ib.reqHistoricalData(
                    contract,
                    endDateTime=end_datetime_str,
                    durationStr=duration_str,
                    barSizeSetting=bar_size,
                    whatToShow=what_to_show,
                    useRTH=use_rth,
                    formatDate=1,
                    keepUpToDate=False
                )

                if not bars:
                    print(f"No data returned for {symbol} ending at {current_end_date}.")
                    break

                # Convert bars to DataFrame
                df = util.df(bars)
                df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)  # Remove timezone info
                df.set_index('date', inplace=True)
                df = df[['close']]
                df.rename(columns={'close': symbol}, inplace=True)

                # Append to list
                data_frames.append(df)

                # Update current_end_date for next iteration
                earliest_date = df.index.min()
                earliest_date = earliest_date.replace(tzinfo=None)  # Ensure timezone-naive
                current_end_date = earliest_date - timedelta(seconds=1)

                print(f"Fetched {len(df)} records. Next end_date: {current_end_date}")

                # Sleep to comply with rate limits
                time.sleep(sleep_interval)

            # Concatenate all DataFrames
            if data_frames:
                data = pd.concat(data_frames)
                data.sort_index(inplace=True)
                # Filter data within the start_date and end_date
                data = data[(data.index >= start_date) & (data.index <= end_date)]
                print(f"Total records fetched for {symbol}: {len(data)}")
            else:
                print(f"No data fetched for symbol {symbol}")
                data = pd.DataFrame()

            return data

        except Exception as e:
            print(f"Error fetching data for symbol {symbol}: {e}")
            return pd.DataFrame()
        finally:
            self.disconnect()


if __name__ == "__main__":
    # Define date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Last 90 days

    # Initialize DataLoader
    data_loader = DataLoader(ib_port=7497, client_id=1)

    # Fetch data for GLD
    gld_data = data_loader.fetch_data(
        symbol='GDX',
        start_date=start_date,
        end_date=end_date,
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=True
    )

    print(gld_data)
