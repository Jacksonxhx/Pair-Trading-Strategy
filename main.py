import pprint
from ib_insync import *
import pandas as pd
from datetime import datetime, timedelta

from PortfolioManagement.portfolio_manager import PortfolioManager
from Data.data_loader import DataLoader
from RegressionModel.regression_model import RegressionModel
from Strategy.strategy import PairTradingStrategy
from Backtesting.backtesting import Backtester
from Utils.main_utils import save_backtest_results, load_config


def backtest(
        config,
        end_date: datetime = datetime.now() - timedelta(days=1)
    ):

    # Import configuration
    time_scale = config['data']['time_length_days']
    commodity1 = config['data']['commodities'][0]
    commodity2 = config['data']['commodities'][1]
    bar_size = config['data']['time_scale']
    window = config['strategy']['window']
    z_threshold = config['strategy']['z_threshold']
    initial_capital = config['capital']['initial_capital']
    transaction_cost = config['capital']['transaction_cost']
    ib_port = config['credentials']['ib_port']
    client_id = config['credentials']['client_id']
    training_threshold = config['data']['training_threshold']

    # Define date range
    start_date = end_date - timedelta(days=time_scale)

    # Initialize DataLoader
    data_loader = DataLoader(ib_port=ib_port, client_id=client_id, data_dir='Data/commodity_data/')

    # Fetch data for GLD
    commodity_1_data = data_loader.fetch_data(
        symbol=commodity1,
        start_date=start_date,
        end_date=end_date,
        bar_size=bar_size,
        what_to_show='TRADES',
        use_rth=True
    )

    # Fetch data for GDX
    commodity_2_data = data_loader.fetch_data(
        symbol=commodity2,
        start_date=start_date,
        end_date=end_date,
        bar_size=bar_size,
        what_to_show='TRADES',
        use_rth=True
    )

    # Merge data
    data = pd.concat([commodity_1_data, commodity_2_data], axis=1).dropna()

    # Split data into training and testing
    training_data = data.iloc[:-int(len(data) / training_threshold)]
    testing_data = data.iloc[-int(len(data) / training_threshold):]

    # Regression Model
    regression_model = RegressionModel(training_data)
    hedge_ratio, alpha = regression_model.linear_fit()

    # Strategy
    strategy = PairTradingStrategy(testing_data, hedge_ratio=hedge_ratio, alpha=alpha, window=window, z_threshold=z_threshold)
    signals = strategy.generate_signals()

    # Backtesting
    backtester = Backtester(testing_data, signals, hedge_ratio, alpha, initial_capital=initial_capital, transaction_cost=transaction_cost)
    results = backtester.run_backtest()
    performance = backtester.evaluate_performance()

    total_datapoints = len(training_data) + len(testing_data)
    save_backtest_results(config, performance, total_datapoints)

    print("Backtest Performance:")
    for key, value in performance.items():
        print(f"{key}: {value}")

    # Plot returns and positions
    backtester.plot_results()
    backtester.plot_positions()


def paper_trade():
    # Portfolio Management (Commented out to prevent real trades)
    # ib = IB()
    # ib.connect('127.0.0.1', 7497, clientId=1)
    # portfolio_manager = PortfolioManager(ib, hedge_ratio, alpha)
    # for index, signal in signals['positions'].iteritems():
    #     portfolio_manager.rebalance(signal)
    # ib.disconnect()
    pass


if __name__ == "__main__":
    config = load_config()
    # print(config)

    backtest(config)

