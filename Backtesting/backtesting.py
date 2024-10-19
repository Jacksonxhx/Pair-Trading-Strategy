import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
        # Prepare data
        self.data['positions'] = self.signals['positions'].cumsum()

        # Calculate positions in monetary terms
        # Allocate half of the capital to each leg
        capital_per_leg = self.initial_capital / 2

        # Number of shares for each leg
        self.data['num_shares_GLD'] = (capital_per_leg / self.data['GLD']) * self.data['positions'].shift(1)
        self.data['num_shares_GDX'] = -(capital_per_leg / (self.data['GDX'] * self.hedge_ratio)) * self.data['positions'].shift(1)

        # Compute PnL for each leg
        self.data['pnl_GLD'] = self.data['num_shares_GLD'] * self.data['GLD'].pct_change()
        self.data['pnl_GDX'] = self.data['num_shares_GDX'] * self.data['GDX'].pct_change()

        # Total PnL
        self.data['pnl_total'] = self.data['pnl_GLD'] + self.data['pnl_GDX']

        # Subtract transaction costs when positions change
        self.data['transaction_costs'] = abs(self.signals['positions']) * self.transaction_cost * self.initial_capital

        # Net PnL
        self.data['net_pnl'] = self.data['pnl_total'] - self.data['transaction_costs']

        # Cumulative PnL
        self.data['cumulative_pnl'] = self.data['net_pnl'].cumsum() + self.initial_capital

        self.results = self.data['cumulative_pnl']
        self.positions = self.data['positions']

        return self.results

    def evaluate_performance(self):
        total_return = self.results.iloc[-1] - self.initial_capital
        total_return_pct = (self.results.iloc[-1] / self.initial_capital - 1) * 100
        days = (self.data.index[-1] - self.data.index[0]).days
        annualized_return = ((self.results.iloc[-1] / self.initial_capital) ** (252 / len(self.results)) - 1) * 100
        annualized_vol = self.data['net_pnl'].std() * np.sqrt(252)
        sharpe_ratio = (self.data['net_pnl'].mean() / self.data['net_pnl'].std()) * np.sqrt(252)

        return {
            'Total Return ($)': total_return,
            'Total Return (%)': total_return_pct,
            'Annualized Return (%)': annualized_return,
            'Annualized Volatility ($)': annualized_vol,
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
