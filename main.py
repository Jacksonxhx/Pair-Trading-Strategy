import pprint
from ib_insync import *
import pandas as pd
from datetime import datetime, timedelta
from Data.data_loader import DataLoader
from RegressionModel.regression_model import RegressionModel
from Strategy.strategy import PairTradingStrategy
from PortfolioManagement.portfolio_manager import PortfolioManager
from Backtesting.backtesting import Backtester


# TODO:
#   把backtest和real trading分开，使用training获取的数据和model，然后做live，做live的同时把当天数据重新扔进去做修正
def main():
    # Define date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Last 90 days

    # Initialize DataLoader
    data_loader = DataLoader(ib_port=7497, client_id=1, data_dir='data')

    # Fetch data for GLD
    gld_data = data_loader.fetch_data(
        symbol='GLD',
        start_date=start_date,
        end_date=end_date,
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=True
    )

    # Fetch data for GDX
    gdx_data = data_loader.fetch_data(
        symbol='GDX',
        start_date=start_date,
        end_date=end_date,
        bar_size='1 min',
        what_to_show='TRADES',
        use_rth=True
    )

    # Merge data
    data = pd.concat([gld_data, gdx_data], axis=1).dropna()

    # Split data into training and testing
    training_data = data.iloc[:-int(len(data) / 3)]
    testing_data = data.iloc[-int(len(data) / 3):]

    # Regression Model
    regression_model = RegressionModel(training_data)
    hedge_ratio, alpha = regression_model.fit()

    # Strategy
    strategy = PairTradingStrategy(testing_data, hedge_ratio, alpha)
    signals = strategy.generate_signals()

    # Backtesting
    initial_capital = 100000  # Adjust as needed
    backtester = Backtester(testing_data, signals, hedge_ratio, alpha, initial_capital=initial_capital)
    results = backtester.run_backtest()
    performance = backtester.evaluate_performance()

    print("Backtest Performance:")
    for key, value in performance.items():
        print(f"{key}: {value}")

    # Plot returns and positions
    backtester.plot_results()
    backtester.plot_positions()

    # Portfolio Management (Commented out to prevent real trades)
    # ib = IB()
    # ib.connect('127.0.0.1', 7497, clientId=1)
    # portfolio_manager = PortfolioManager(ib, hedge_ratio, alpha)
    # for index, signal in signals['positions'].iteritems():
    #     portfolio_manager.rebalance(signal)
    # ib.disconnect()


if __name__ == "__main__":
    main()


