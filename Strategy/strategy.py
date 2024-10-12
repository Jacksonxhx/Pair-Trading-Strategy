import pandas as pd
import numpy as np


class PairTradingStrategy:
    def __init__(self, data, hedge_ratio, alpha, z_threshold=3, window=100):
        self.data = data.copy()
        self.hedge_ratio = hedge_ratio
        self.alpha = alpha
        self.z_threshold = z_threshold
        self.window = window
        self.signals = pd.DataFrame(index=self.data.index)

    def generate_signals(self):
        epsilon = 1e-8  # Small value to avoid division by zero

        # Calculate spread
        self.data.loc[:, 'spread'] = self.data['GLD'] - self.hedge_ratio * self.data['GDX'] + self.alpha

        # Calculate rolling mean and std
        self.data.loc[:, 'spread_mean'] = self.data['spread'].rolling(window=self.window).mean()
        self.data.loc[:, 'spread_std'] = self.data['spread'].rolling(window=self.window).std()

        # Replace zero std with epsilon
        self.data.loc[:, 'spread_std'] = self.data['spread_std'].replace(0, epsilon)

        # Compute z-score
        self.data.loc[:, 'z_score'] = (self.data['spread'] - self.data['spread_mean']) / self.data['spread_std']

        # Initialize positions
        self.signals['positions'] = 0

        # Generate signals based on z-score
        self.signals.loc[self.data['z_score'] > self.z_threshold, 'positions'] = -1
        self.signals.loc[self.data['z_score'] < -self.z_threshold, 'positions'] = 1

        # Forward-fill positions to maintain positions until exit signal
        self.signals['positions'] = self.signals['positions'].ffill().fillna(0)

        # Calculate position changes (trade signals)
        self.signals['positions'] = self.signals['positions'].diff().fillna(0)

        return self.signals
