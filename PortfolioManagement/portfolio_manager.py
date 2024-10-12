from ib_insync import *
import pandas as pd


class PortfolioManager:
    def __init__(self, ib, hedge_ratio):
        self.ib = ib
        self.hedge_ratio = hedge_ratio
        self.positions = {'GLD': 0, 'GDX': 0}

    def execute_trade(self, symbol, action, quantity):
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        return trade

    def rebalance(self, signal):
        if signal == 1:
            # Buy GLD, Sell GDX
            self.execute_trade('GLD', 'BUY', 100)
            self.execute_trade('GDX', 'SELL', int(100 * self.hedge_ratio))
        elif signal == -1:
            # Sell GLD, Buy GDX
            self.execute_trade('GLD', 'SELL', 100)
            self.execute_trade('GDX', 'BUY', int(100 * self.hedge_ratio))
        # No action for 0 signal

    def close_positions(self):
        """
        Sell all the stocks by the end of the day
        """
        # Close GLD position
        if self.positions['GLD'] != 0:
            action = 'SELL' if self.positions['GLD'] > 0 else 'BUY'
            self.execute_trade('GLD', action, abs(self.positions['GLD']))
        # Close GDX position
        if self.positions['GDX'] != 0:
            action = 'SELL' if self.positions['GDX'] > 0 else 'BUY'
            self.execute_trade('GDX', action, abs(self.positions['GDX']))
