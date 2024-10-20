import json
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def save_to_json(data, filename='output_data.json'):
    """
    Save the DataFrame to a local JSON file.

    Parameters:
    -----------
    data : pd.DataFrame
        The DataFrame to be saved.
    filename : str, optional
        The name of the file to save the data to. Default is 'output_data.json'.
    """
    # Convert the DataFrame to a dictionary
    data_dict = data.to_dict(orient='records')

    # Save the dictionary to a JSON file
    with open(filename, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)

    print(f"Data successfully saved to {filename}")


class Backtester:
    def __init__(self, data, signals, hedge_ratio, alpha, initial_capital, transaction_cost):
        self.data = data.copy()
        self.signals = signals.copy()
        self.hedge_ratio = hedge_ratio
        self.alpha = alpha
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.results = None

    def run_backtest(self):
        # Copy data to avoid modifying the original DataFrame
        self.data = self.data.copy()
        self.data['positions'] = self.signals['positions']

        # Initialize columns for calculations
        self.data['num_shares_GLD'] = 0.0
        self.data['num_shares_GDX'] = 0.0
        self.data['cash'] = self.initial_capital
        self.data['holdings'] = 0.0
        self.data['total_asset'] = 0.0
        self.data['transaction_costs'] = 0.0
        self.data['pnl'] = 0.0

        # Variables to keep track of current positions and cash
        current_cash = self.initial_capital
        current_num_shares_GLD = 0.0
        current_num_shares_GDX = 0.0

        for i in range(len(self.data)):
            print(f"\n--- Iteration {i} ---")
            # Get the index (date) and current row
            index = self.data.index[i]
            row = self.data.iloc[i]

            # Get current prices
            price_GLD = row['GLD']
            price_GDX = row['GDX']

            # Get the position signal (1, 0, -1)
            position = row['positions']

            # Determine if we need to adjust positions
            if i > 0:
                prev_position = self.data['positions'].iloc[i - 1]
            else:
                prev_position = 0

            if position != prev_position:
                # Need to rebalance positions
                # First, calculate proceeds from selling existing positions
                proceeds_GLD = current_num_shares_GLD * price_GLD
                proceeds_GDX = current_num_shares_GDX * price_GDX
                current_cash += proceeds_GLD + proceeds_GDX

                # Calculate transaction costs for selling
                transaction_costs = (abs(proceeds_GLD) + abs(proceeds_GDX)) * self.transaction_cost

                current_cash -= transaction_costs

                # Update transaction costs
                self.data.at[index, 'transaction_costs'] += transaction_costs

                # Calculate new positions
                capital_per_leg = current_cash / 2  # Allocate half of the cash to each leg

                # When position is +1: Long GLD, Short GDX
                # When position is -1: Short GLD, Long GDX
                # When position is 0: No positions

                # Long GLD / Short GDX
                if position == 1:
                    num_shares_GLD = capital_per_leg / price_GLD
                    num_shares_GDX = -(capital_per_leg / (price_GDX * self.hedge_ratio))
                # Short GLD / Long GDX
                elif position == -1:
                    num_shares_GLD = -(capital_per_leg / price_GLD)
                    num_shares_GDX = capital_per_leg / (price_GDX * self.hedge_ratio)
                else:
                    num_shares_GLD = 0.0
                    num_shares_GDX = 0.0

                # Calculate cost to buy new positions
                cost_GLD = num_shares_GLD * price_GLD
                cost_GDX = num_shares_GDX * price_GDX

                # Calculate transaction costs for buying
                transaction_costs = (abs(cost_GLD) + abs(cost_GDX)) * self.transaction_cost

                current_cash -= (cost_GLD + cost_GDX + transaction_costs)

                # Update transaction costs
                self.data.at[index, 'transaction_costs'] += transaction_costs

                # Update current positions
                current_num_shares_GLD = num_shares_GLD
                current_num_shares_GDX = num_shares_GDX
            else:
                print("No position change. Holding current positions.")

            # Update holdings value
            holdings = current_num_shares_GLD * price_GLD + current_num_shares_GDX * price_GDX

            # Update total asset value
            total_asset = current_cash + holdings
            print(f"Total Asset Value: {total_asset}")

            # Calculate PnL
            if i > 0:
                prev_total_asset = self.data['total_asset'].iloc[i - 1]
                pnl = total_asset - prev_total_asset
            else:
                pnl = total_asset - self.initial_capital

            # Update the DataFrame
            self.data.at[index, 'num_shares_GLD'] = current_num_shares_GLD
            self.data.at[index, 'num_shares_GDX'] = current_num_shares_GDX
            self.data.at[index, 'cash'] = current_cash
            self.data.at[index, 'holdings'] = holdings
            self.data.at[index, 'total_asset'] = total_asset
            self.data.at[index, 'pnl'] = pnl

        # Calculate cumulative PnL and returns
        self.data['cumulative_pnl'] = self.data['total_asset'] - self.initial_capital
        self.data['returns'] = self.data['total_asset'].pct_change().fillna(0)

        # Save results
        self.results = self.data['total_asset']
        self.positions = self.data['positions']
        self.returns = self.data['returns']

        return self.results

    def evaluate_performance(self):
        total_minutes = len(self.data)

        # Risk-free rate settings
        risk_free_rate_annual = 0.03
        minutes_per_day = 390
        trading_days_per_year = 252
        minutes_per_year = minutes_per_day * trading_days_per_year
        risk_free_rate_per_minute = risk_free_rate_annual / minutes_per_year

        # Total return calculations
        final_portfolio_value = self.results.iloc[-1]
        total_return = final_portfolio_value - self.initial_capital
        total_return_pct = (final_portfolio_value / self.initial_capital - 1) * 100

        # Annualized return
        cumulative_return = final_portfolio_value / self.initial_capital
        annualized_return = (cumulative_return ** (minutes_per_year / total_minutes) - 1) * 100

        # Per-minute returns
        minute_returns = self.returns  # Assuming self.returns is per-minute return calculated in run_backtest

        # Annualized volatility
        annualized_volatility = minute_returns.std() * np.sqrt(minutes_per_year) * 100  # Convert to percentage

        # Sharpe Ratio
        excess_returns = minute_returns - risk_free_rate_per_minute
        sharpe_ratio = (excess_returns.mean() / minute_returns.std()) * np.sqrt(minutes_per_year)

        return {
            'Total Return ($)': total_return,
            'Total Return (%)': total_return_pct,
            'Annualized Return (%)': annualized_return,
            'Annualized Volatility (%)': annualized_volatility,
            'Sharpe Ratio': sharpe_ratio
        }

    def plot_results(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.results.index, self.results.values, label='Cumulative Net PnL')
        plt.title('Strategy Performance')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.show()

    def plot_positions(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.positions.index, self.positions.values, label='Position Holdings')
        plt.title('Position Holdings Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Positions')
        plt.legend()
        plt.show()
